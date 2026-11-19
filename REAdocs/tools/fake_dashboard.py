"""Fake V4 S dashboard for the mySPIN TCP session.

Runs the real myspin PhoneProjection (the phone side) against a scripted dashboard over a local TCP connection and
prints every packet both ways, decoded and in hex. This is how the session setup, frame pacing and joystick encoding
in ../myspin-protocol.md were established (18 Nov 2026).

A scenario is a Python file defining `async def scenario(d)`; `d` offers:
    d.send(op, values)          build with the chosen revision and send
    d.send_raw(op, body_parts)  send a hand-built body (list of bytes)
    d.key(code, action, ms)     DASH_CUSTOM kind 5 joystick event
    d.setup()                   the standard handshake (HELLO ... first FRAME_WANTED)
    d.C, d.rev, d.sleep         myspin.catalog, the Revision object, asyncio.sleep

Run inside the container (see run.sh):
    ./run.sh fake_dashboard.py --scenario scenarios/joystick.py
"""
import argparse
import asyncio
import json
import os
import struct
import sys
import time

sys.path.insert(0, "/target")
from myspin import catalog as C, fields as F, revisions as R  # noqa: E402
from myspin.phone import PhoneProjection  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

NAMES = {v: k for k, v in vars(C.Op).items() if isinstance(v, int)}
T0 = time.monotonic()


def ts():
    return f"{time.monotonic() - T0:6.3f}"


class Screen:
    """The `frames` object PhoneProjection needs. `version` must be a property: as a plain method the feed compares
    bound methods, never sees a change, and held incremental requests are never answered (found the hard way)."""

    def __init__(self):
        self.v = 0

    @property
    def version(self):
        return (self.v,)

    def render(self, w, h):
        im = Image.new("RGB", (w, h), (0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), f"Hello World {self.v}", fill=(255, 255, 255))
        return im

    def on_key(self, key, action):
        print(ts(), "UI    on_key", key, action, flush=True)
        self.v += 1

    def on_frame_sent(self, size):
        pass


def phone_log(event, **fields):
    print(ts(), "LOG  ", event, {k: (v[:16] if isinstance(v, bytes) else v) for k, v in fields.items()}, flush=True)


class Dashboard:
    def __init__(self, reader, writer, rev, frames):
        self.r, self.w, self.rev, self.frames_left = reader, writer, rev, frames
        self.C, self.sleep = C, asyncio.sleep

    def _decode(self, op, body):
        try:
            d = self.rev.parse(op, body)
            if "picture" in d:
                d["picture"] = f"<{len(d['picture'])} bytes {d['picture'][:4].hex()}>"
            return d
        except Exception as e:
            return f"raw={body[:40].hex()} ({e})"

    def _out(self, op, what, data):
        print(ts(), f"DASH> {op:3d} {NAMES.get(op, '?'):15s}", what, "| hex", data[:48].hex(), flush=True)
        self.w.write(data)

    def send(self, op, values):
        self._out(op, values, self.rev.build(op, values))

    def send_raw(self, op, parts):
        self._out(op, "raw", F.seal(op, parts))

    def key(self, code, action, ms=0):
        self._out(67, {"key": code, "action": action, "ms": ms},
                  F.seal(67, [struct.pack("<BHH", 5, action, 5), struct.pack("<BI", code, ms)]))

    async def setup(self):
        rv = self.rev.label.split(".")
        self.send(C.Op.HELLO, {"major": int(rv[0]), "minor": int(rv[1]), "patch": 0})
        await asyncio.sleep(0.1)
        self.send(C.Op.DISPLAY_INFO, {"title": "Ducati", "width": 848, "height": 304, "phys_width": 150,
                                      "phys_height": 54, "opaque": 0, "pixel_format": 4, "byte_order": 1,
                                      "preferred": 1, "level": 0, "capabilities": 1, "list_a": [], "list_b": [],
                                      "tail_a": 0, "tail_b": 0})
        await asyncio.sleep(0.1)
        if self.rev.label == "2.0":
            self.send(C.Op.INIT_EXTENSION, {"first": 1, "second": 2})
        if self.rev.label != "1.1":                     # 1.1 has no DASH_READY / PHONE_READY exchange
            self.send(C.Op.DASH_READY, {"ok": 1})
            await asyncio.sleep(0.1)
        self.send(C.Op.PIXEL_SET, {"pixel_format": 4, "byte_order": 1, "level": 0})
        await asyncio.sleep(0.05)
        self.send(C.Op.CODING_SET, {"coding": 1})
        await asyncio.sleep(0.05)
        self.send(C.Op.FRAME_WANTED, {"screen": 0, "x": 0, "y": 0, "width": 848, "height": 304, "incremental": 0})
        await asyncio.sleep(0.3)

    async def receive_loop(self):
        while True:
            hdr = await self.r.readexactly(9)
            op, word, length = struct.unpack("<BII", hdr)
            body = await self.r.readexactly(length)
            print(ts(), f"PHONE> {op:3d} {NAMES.get(op, '?'):15s} word={word} len={length}", self._decode(op, body),
                  "| hex", (hdr + body)[:40].hex(), flush=True)
            if op == C.Op.PING:
                self.send(C.Op.PONG, self.rev.parse(op, body))
            elif op == C.Op.FRAME and self.frames_left > 1:
                # like the real dashboard: one request outstanding, the next one after each FRAME
                self.frames_left -= 1
                self.send(C.Op.FRAME_WANTED, {"screen": 0, "x": 0, "y": 0, "width": 848, "height": 304,
                                              "incremental": 1})


async def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario", default=os.path.join(os.path.dirname(__file__), "scenarios", "handshake.py"))
    ap.add_argument("--rev", default="1.2", choices=["1.1", "1.2", "2.0"], help="protocol revision the dashboard announces")
    ap.add_argument("--frames", type=int, default=50, help="how many frames to request in total")
    ap.add_argument("--tail", type=float, default=1.0, help="seconds to keep listening after the scenario")
    ap.add_argument("--bt-info", default=None, help='e.g. "[HFP,A2DP]ESP32" (sent as PHONE_CUSTOM kind 1 code 1)')
    a = ap.parse_args()

    rev = R.REVISIONS[tuple(int(x) for x in a.rev.split("."))]
    ns = {}
    exec(open(a.scenario).read(), ns)
    done = asyncio.get_running_loop().create_future()

    async def on_conn(reader, writer):
        d = Dashboard(reader, writer, rev, a.frames)
        rx = asyncio.create_task(d.receive_loop())
        try:
            await ns["scenario"](d)
        finally:
            await asyncio.sleep(a.tail)
            rx.cancel()
            writer.close()
            done.set_result(None)

    srv = await asyncio.start_server(on_conn, "127.0.0.1", 0)
    r, w = await asyncio.open_connection("127.0.0.1", srv.sockets[0].getsockname()[1])
    phone = PhoneProjection(r, w, Screen(), phone_log, 80, a.bt_info, [1, 2, 3])
    run = asyncio.create_task(phone.run())
    await done
    try:
        await asyncio.wait_for(run, 3)
    except Exception as e:
        print(ts(), "phone session ended:", type(e).__name__, e)
    print("packet counts:", json.dumps({str(k): v for k, v in dict(phone.packet_counts).items()}))


asyncio.run(main())
