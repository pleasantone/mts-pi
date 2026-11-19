"""Recovers the string/int/tuple constants of each Cython module.

Cython 3.3 stores its string table LZSS-compressed, so `strings` on the .so shows little, and m_size is 0 (state is a
static global). After import, the decompressed objects are pointed to from the module's own writable segments: scan
those words and keep the ones whose ob_type is str/bytes/int/tuple/float/frozenset. Reads /proc/self/mem, so a bad
pointer cannot crash the process. Diffing whole-process memory before/after import was tried first and was too noisy."""
import sys, ctypes, importlib, struct; sys.path.insert(0, "/target")
mods=["fields","catalog","revisions","discovery","control","feed","pixels","phone","tally"]
for n in mods: importlib.import_module("myspin."+n)
mem=open("/proc/self/mem","rb",0)
def rd(a,n):
    try: mem.seek(a); return mem.read(n)
    except Exception: return None
def q(a):
    b=rd(a,8); return struct.unpack("<Q",b)[0] if b and len(b)==8 else None
want={id(str):"str",id(bytes):"bytes",id(int):"int",id(tuple):"tuple",id(float):"float",id(frozenset):"frozenset"}
lines=open("/proc/self/maps").read().splitlines()
for n in mods:
    regs=[]
    for i,l in enumerate(lines):
        p=l.split()
        if len(p)>5 and p[5].endswith(f"/{n}.cpython-313-aarch64-linux-gnu.so") and "rw" in p[1]:
            regs.append(p[0])
            if i+1<len(lines) and len(lines[i+1].split())==5: regs.append(lines[i+1].split()[0])
    print(f"\n######## {n} regions {regs}")
    seen=set()
    for r in regs:
        a,b=(int(x,16) for x in r.split("-"))
        data=rd(a,b-a)
        for off in range(0,len(data)-7,8):
            p=struct.unpack_from("<Q",data,off)[0]
            if p<0x10000 or p in seen: continue
            t=q(p+8)
            if t in want:
                seen.add(p)
                o=ctypes.cast(p,ctypes.py_object).value
                if isinstance(o,str) and (o.startswith("__pyx") or o.startswith("myspin.")): continue
                print(want[t], repr(o)[:400])
