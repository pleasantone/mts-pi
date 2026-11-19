"""Prints every message layout in myspin.catalog.LAYOUTS (field name, wire type, revisions) and the three protocol
revisions with the IDENTITY each one sends. This is where the opcode table in myspin-protocol.md comes from."""
import sys; sys.path.insert(0, "/target")
from myspin import fields, catalog, revisions
def kd(k):
    n=type(k).__name__
    d={a:getattr(k,a) for a in dir(k) if not a.startswith('__') and not callable(getattr(k,a))}
    for a,v in list(d.items()):
        if hasattr(v,'__dict__') or type(v).__module__=='myspin.fields': d[a]=kd(v)
    return f"{n}{d}"
for nm in ("U8","U16","U32","U64","TEXT"): print(nm, kd(getattr(fields,nm)))
names={v:k for k,v in vars(catalog.Op).items() if isinstance(v,int)}
print("\n# LAYOUTS")
for op, lay in sorted(catalog.LAYOUTS.items()):
    print(f"op {op} {names.get(op)}")
    for f in lay:
        print("   ", f.name, kd(f.kind), "revs=", getattr(f,'revisions',None))
for k in ("DASH_CUSTOM_HEAD","_ACK"):
    print(k,[ (f.name,kd(f.kind)) for f in getattr(catalog,k)])
print("\n# REVISIONS")
for k,r in revisions.REVISIONS.items():
    print(k, {a:getattr(r,a) for a in dir(r) if not a.startswith('__') and not callable(getattr(r,a))})
    try: print("  identity", r.identity())
    except Exception as e: print("  identity err", e)
print("PRE_HELLO", revisions.PRE_HELLO.label if hasattr(revisions.PRE_HELLO,'label') else '')
