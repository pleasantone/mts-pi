# REAdocs: reverse-engineering notes on mySPIN

Research into the protocol between the Ducati Multistrada V4 S dashboard and a mySPIN "phone", recovered from the
closed `myspin/` package in this repository. The goal: an independent phone-side implementation, first in Python
on a Pi 4 / Mac, then standalone on an ESP32 that shows "Hello World" on the dashboard and reacts to the joystick.

| Path | What it is |
| --- | --- |
| [myspin-protocol.md](myspin-protocol.md) | The protocol and API document: Bluetooth control channel, Wi-Fi Direct and discovery, TCP session (every opcode and layout), frames, joystick, test platforms, ESP32 plan, open questions |
| [memory/](memory/MEMORY.md) | Short fact files for the next working session (decisions, findings, open questions), indexed by `MEMORY.md` |
| [tools/](tools/) | The scripts that produced the findings: API and layout dumps, constant recovery, a fake dashboard, a fake control channel |

`myspin-protocol.md` is an export of a living Claude Doc (18 Nov 2026). The two diagrams are redrawn in Mermaid.

## How the findings were obtained

All work was done on a Mac (Apple silicon) on 18 Nov 2026. Nothing was tried on the bike.

1. **Identify the binaries.** The nine modules (`fields`, `catalog`, `revisions`, `control`, `discovery`, `phone`,
   `feed`, `pixels`, `tally`) are Cython 3.3.1 extensions for CPython 3.13 aarch64 Linux. Their string constants are
   LZSS-compressed, so `strings` shows little.
2. **Load them.** In a `python:3.13-slim` linux/arm64 container (native on Apple silicon, numpy/Pillow/PyAV added),
   the modules import normally. `tools/dump_api.py` and `tools/dump_layouts.py` print classes, signatures, the
   opcode table and every message layout per protocol revision.
3. **Recover the string table.** `tools/recover_constants.py` scans each module's writable segments for pointers to
   live `str`/`int`/`tuple` objects. That gave the JSON keys and message names of the control channel, the
   announcement keys, error texts and log events. A whole-process memory diff was tried first and was too noisy.
4. **Exercise the encoders.** `tools/probe_fields.py` and `tools/probe_discovery_pixels.py` call the encoders and
   parsers directly to get exact bytes, and find which inputs are rejected.
5. **Drive the phone code against fake peers.** `tools/fake_control.py` (Bluetooth JSON) and
   `tools/fake_dashboard.py` (TCP session) run the real `PhoneControl` / `PhoneProjection` against a scripted
   dashboard and log every packet. The handshake, the frame pacing (incremental requests held until the screen
   changes) and the joystick encoding (DASH_CUSTOM kind 5, action in the `code` field) were found this way.
6. **Cross-check with the open code.** `mtspi/session.py`, `mtspi/bluez.py`, `mtspi/bridge.py` and the README give
   what was seen on the real bike: the RFCOMM service, the Wi-Fi Direct join, the real joystick behaviour.

**Confidence.** Everything the phone sends is observed. What the dashboard sends is inferred: it is what the phone
code accepts, consistent with the bike notes in this repository. No capture from a real dashboard was available.

## Running the tools

Needs Docker with linux/arm64. `tools/run.sh` builds the image on first use and mounts `myspin/` read-only:

```bash
cd REAdocs/tools
./run.sh dump_layouts.py
./run.sh fake_dashboard.py --scenario scenarios/joystick.py           # --rev 1.1|1.2|2.0
./run.sh fake_control.py '{"phoneDetectRequest":{"type":"iviDetectResponse","version":"3","payload":{}}}'
```

`paddle_game.py` is a reference game as a mySPIN `frames` object (the Track 1 "Hello World" capstone — a paddle
game played with the joystick against the computer). Play it through the real session and record the result:

```bash
# writes the frames the dashboard received to a GIF (needs a writable output mount, so not via run.sh):
docker run --rm --platform linux/arm64 -w /tools \
  -v "$PWD/../../myspin:/target/myspin:ro" -v "$PWD:/tools:ro" -v /tmp:/out \
  myspin-re python -I /tools/fake_dashboard.py --game --seconds 16 --gif /out/paddle.gif
```

`tools/paddle-demo.gif` is a recording of exactly that: the game rendered by the phone code, JPEG-encoded, carried
over the mySPIN FRAME messages, and decoded by the fake dashboard — no bike or ESP32 involved.

`fake_control.py` takes a JSON object mapping each phone message type to the bike's reply (or a list of replies);
`myspin-protocol.md` lists the full exchange to script.

## Licence note

`myspin/LICENSE.txt` allows personal, non-commercial use and study, and says the files exist for interoperability.
These notes describe the protocol for that purpose. They contain no code from the binaries, and the tools only load
the binaries at run time.
