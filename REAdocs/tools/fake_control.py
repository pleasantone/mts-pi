"""Fake dashboard for the Bluetooth control channel: runs PhoneControl.negotiate() with a scripted bike.
Argument: a JSON object mapping each phone message type to the bike reply (or list of replies). Example in README.md."""
import sys, asyncio, json; sys.path.insert(0, "/target")
from myspin.control import PhoneControl
SCRIPT = json.loads(sys.argv[1])   # list of bike lines to send after each phone line
class W:
    def __init__(s, r): s.r=r; s.buf=b""; s.n=0
    def write(s,b):
        s.buf+=b
        while b"\n" in s.buf:
            line,s.buf=s.buf.split(b"\n",1); print("PHONE>", line.decode(), flush=True)
            msg=json.loads(line)
            reply = SCRIPT.get(msg.get("type"))
            if reply is not None:
                for rr in (reply if isinstance(reply,list) else [reply]):
                    rr=dict(rr); rr.setdefault("id", msg.get("id"))
                    print("BIKE >", json.dumps(rr), flush=True); s.r.feed_data((json.dumps(rr)+"\n").encode())
    async def drain(s): pass
    def close(s): pass
def log(ev, **k): print("LOG  ", ev, k, flush=True)
async def main():
    r=asyncio.StreamReader(); w=W(r)
    pc=PhoneControl(r,w,log)
    try: print("RESULT", await asyncio.wait_for(pc.negotiate(timeout=3), 4))
    except Exception as e: print("EXC", type(e).__name__, e)
    try: await pc.notify_wlan("CONNECTED")
    except Exception as e: print("notify EXC", e)
asyncio.run(main())
