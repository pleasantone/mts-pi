"""Calls the field encoders and Revision.build for each opcode, and the control-channel line builder, to get exact bytes."""
import sys, asyncio; sys.path.insert(0, "/target")
from myspin import fields as F, catalog as C, revisions as R, control, discovery
print("TEXT ascii", F.TEXT.pack("Hi"), "utf8", F.TEXT.pack("è"))
for raw in [b"\x01\x03\x00abc", b"\x02\x03\x00ab\xe8", b"\x01\x00\x00"]:
    try: print("try", raw, F.TEXT.unpack(F.Cursor(raw)))
    except Exception as e: print("try", raw, "ERR", e)
print("Blob32", F.Blob(F.U32).pack(b"xyz"), "Fixed3", F.Fixed(3).pack(b"ita"))
print("Seq", F.Seq(F.U8,F.U16).pack([1,2]))
print("seal", F.seal(1, F.pack_parts(C.LAYOUTS[1], {"major":2,"minor":0,"patch":0})).hex())
for lbl,r in R.REVISIONS.items():
    print("rev",lbl)
    for op in (2,12,14,18,22,24,26,31,36,54,61,68,128,129,169):
        try:
            vals={f.name:0 for f in r.shape(op)}
            if op==14: vals=r.identity()
            if op==26: vals.update(picture=b"JPG"); 
            if op==54: vals["codes"]=[1,2]
            if op==68: vals["data"]=b"\x01"
            print("  ", op, r.build(op, vals).hex())
        except Exception as e: print("  ",op,"ERR",repr(e))
print("ctrl line", control._line("DETECTED", {"a":1}), control._line("X"), control._line("Y",None,3))
async def rx():
    r=asyncio.StreamReader(); r.feed_data(F.seal(128, F.pack_parts(C.LAYOUTS[128],{"seq":7}))); r.feed_eof()
    print("receive", await F.receive(r))
asyncio.run(rx())
