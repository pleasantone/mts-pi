"""Feeds UDP announcements to discovery.read_announcement (which keys are required, what is rejected) and encodes a
tiny image with every coding / pixel format / byte order through pixels.encode."""
import sys, json, zlib; sys.path.insert(0, "/target")
from myspin import discovery as D, pixels as P
from PIL import Image
for d in [{"hostname":"192.168.49.1","port":5000,"version":"1.2","identification":"x"},
          {"hostname":"192.168.49.1","port":"5000","version":2,"identification":"DUCATI"},
          {"hostname":"","hostname_v6":"fe80::1","port":5000,"version":1,"identification":"x"},
          {"hostname":"bike.local","port":5000,"version":1},
          {"hostname":"192.168.49.1","port":70000,"version":1,"identification":"x"}]:
    try: print("ANN", json.dumps(d), "->", D.read_announcement(json.dumps(d).encode(), "192.168.49.1"))
    except Exception as e: print("ANN", json.dumps(d), "-> ERR", e)
try: print("ANN nul", D.read_announcement(json.dumps({"hostname":"h","port":1,"version":1,"identification":"i"}).encode()+b"\x00\r\n", "1.1.1.1"))
except Exception as e: print("ERR",e)
im=Image.new("RGB",(4,2),(255,0,0)); im.putpixel((1,0),(0,255,0)); im.putpixel((2,0),(0,0,255))
for coding in (1,2,4):
  for fmt,order in [(2,1),(2,2),(3,1),(3,2),(4,1),(4,2)]:
    try:
        b=P.encode(im, P.Recipe(4,2,fmt,order,coding,80))
        if coding==2: b2=zlib.decompress(b); print(f"coding {coding} fmt {fmt} order {order}: zlib {len(b)}B -> {b2[:16].hex()}")
        elif coding==4: print(f"coding {coding} fmt {fmt} order {order}: raw {len(b)}B {b[:16].hex()}")
        else: print(f"coding {coding} fmt {fmt} order {order}: {len(b)}B {b[:4].hex()}")
    except Exception as e: print(f"coding {coding} fmt {fmt} order {order}: ERR {e}")
for pref,cap in [(1,1),(2,3),(4,7),(1,6),(2,1),(0,7)]:
    try: print("choose_coding pref",pref,"cap",cap,"->",P.choose_coding(pref,cap))
    except Exception as e: print("choose_coding",pref,cap,"ERR",e)
