---
name: re-method
description: How the myspin Cython binaries were analysed (arm64 container, constant recovery, fake peers) and the gotchas found
metadata:
  type: reference
---

- The `myspin/*.so` are Cython 3.3.1, CPython 3.13 aarch64 Linux. They load in `python:3.13-slim` linux/arm64
  under Docker on the Mac; `REAdocs/tools/run.sh` does this (image `myspin-re` with numpy, Pillow, PyAV).
- String constants are LZSS-compressed; module state is static (m_size 0). Recover them by scanning the module's
  writable segments for object pointers (`recover_constants.py`). Whole-process memory diffs were too noisy.
- Dynamic analysis beats static here: drive `PhoneControl` / `PhoneProjection` with scripted peers
  (`fake_control.py`, `fake_dashboard.py`) and read what they send and log.
- Gotcha: the `frames` object's `version` must be a property. As a method, held incremental frame requests are
  never answered.
- The REA MCP tools were not needed; plain Python introspection in the container answered everything.

Related: [[protocol-facts]].
