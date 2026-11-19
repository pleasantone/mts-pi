"""Loads every myspin module and prints classes, signatures and module constants.
Run: ./run.sh dump_api.py  (needs the arm64 Python 3.13 container: the .so files are CPython 3.13 aarch64 Linux)."""
import sys, importlib, inspect, types
sys.path.insert(0, "/target")
mods = ["fields","catalog","tally","revisions","pixels","discovery","feed","control","phone"]
for name in mods:
    try:
        m = importlib.import_module("myspin."+name)
    except Exception as e:
        print("##", name, "IMPORT FAIL", repr(e)); continue
    print("\n######## module", name, "doc:", repr(m.__doc__))
    for k, v in sorted(vars(m).items()):
        if k.startswith("__") and k not in ("__all__",): continue
        if isinstance(v, types.ModuleType): print(" mod", k, v.__name__); continue
        if inspect.isclass(v):
            if v.__module__ != m.__name__: print(" import-class", k, v.__module__); continue
            print(" class", k, "bases", [b.__name__ for b in v.__bases__], "doc:", repr(v.__doc__))
            for a, av in vars(v).items():
                if a.startswith("__") and a not in ("__init__",): continue
                if callable(av) or isinstance(av,(staticmethod,classmethod,property)):
                    f = av.__func__ if isinstance(av,(staticmethod,classmethod)) else av
                    try: sig = str(inspect.signature(f))
                    except Exception: sig = "?"
                    print("    def", a, sig, "|", repr(getattr(f,"__doc__",None)))
                else:
                    print("    attr", a, "=", repr(av)[:400])
        elif callable(v):
            if getattr(v,"__module__",None) not in (m.__name__,None): print(" import", k, getattr(v,"__module__","")); continue
            try: sig = str(inspect.signature(v))
            except Exception: sig = "?"
            print(" def", k, sig, "|", repr(v.__doc__))
        else:
            print(" const", k, "=", repr(v)[:1500])
