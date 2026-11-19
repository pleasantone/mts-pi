#!/bin/bash
# Runs one of these tools inside an arm64 Python 3.13 container, where the myspin .so files can load
# (they are CPython 3.13 aarch64 Linux builds: they do not import on macOS).
# Usage: ./run.sh <script.py> [args...]     e.g. ./run.sh fake_dashboard.py --scenario scenarios/joystick.py
# Needs Docker with linux/arm64 (native on Apple silicon). The image (numpy, Pillow, PyAV) is built on first use.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
IMAGE=${IMAGE:-myspin-re}
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker build -q --platform linux/arm64 -t "$IMAGE" "$HERE" >/dev/null
fi
[ $# -ge 1 ] || { sed -n '2,5p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
SCRIPT=$1; shift
# python -I: isolated mode, so nothing from the working directory shadows the standard library
exec docker run --rm --platform linux/arm64 -w /tools \
    -v "$REPO/myspin:/target/myspin:ro" -v "$HERE:/tools:ro" \
    "$IMAGE" python -I "/tools/$SCRIPT" "$@"
