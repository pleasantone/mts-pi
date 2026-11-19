# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

MTS Pi puts Apple CarPlay on the original dashboard of a Ducati Multistrada V4 S. It runs on a Raspberry Pi 3 A+
with a Carlinkit CPC200-CCPA dongle. To the dashboard, the Pi looks like a phone running Ducati Connect (mySPIN).
To the iPhone, it looks like a car with wireless CarPlay. The target is Raspberry Pi OS Lite 64-bit (Debian 13
"trixie"), Python 3.13, aarch64. Development happens on a Mac "bench", with emulated peers over TCP. README.md is
the user-facing document. Its "Things we learned" and "Known limits" sections record hard-won constraints, so read
them before changing radio, audio or joystick behaviour.

## Commands

There is no build step, linter config or test runner config.

- **Python tests:** each file runs as a script. Its `__main__` block calls every `test_*` function.
  ```bash
  python tests/test_carplay_call.py
  python tests/test_siri.py
  python tests/test_bike_evening.py
  python tests/test_avrcp.py
  python tests/test_snap_race.py     # needs av, numpy, PIL
  ```
  The test functions are plain `assert` functions, so `pytest tests/test_siri.py::test_bridge_siri_from_bike`
  also works if pytest is installed, for running a single test. Tests that import `mtspi.bridge` need `av` and
  `numpy`. `mtspi.bluez` (dbus-fast) is optional: bridge.py falls back to `bluez = None` off the Pi.
- **Shell test:** `bash tests/test_setup_file.sh` tests `system/setup-file.sh` with stub system commands. It needs
  GNU sed, so it runs on Linux only. `image/build.sh` runs it inside the image.
- **Install on a Pi:** `./install.sh` as the normal user (`--name`, `--no-carlinkit`; `--help`). It is
  idempotent. It creates `.venv` with `--system-site-packages`: PIL, numpy and av come from apt; dbus-fast and
  pyusb come from pip.
- **Card image:** `sudo image/build.sh <version>` on an arm64 Linux machine writes `out/mts-pi-<version>.img.xz`.
  CI (`.github/workflows/image.yml`) runs it on `workflow_dispatch` or on a `v*` tag, then uploads the image to a
  (draft) release.
- **On the Pi:** `sudo systemctl restart mtspi-bridge mtspi-hfp`. For logs:
  `journalctl -u mtspi-bridge -u mtspi-hfp -u mtspi-wifi-mode`. Each bridge run also writes JSON-line logs to
  `/var/lib/mtspi/run-*/`.

## Architecture

### Processes (systemd units in `system/units/`)

`install.sh` fills in the `@REPO@`, `@USER@` and `@UID@` placeholders. On the card image the repository lives in
`/opt/mts-pi` and the service user is `mtspi`. Settings come from `/etc/default/mtspi`.

- **mtspi-bridge**: `system/run.sh` → `python -m mtspi.bridge`. This is the main program. `run.sh` maps the env
  settings (`CARLINKIT`, `RADIO`, `BT_NAME`…) to command-line flags.
- **mtspi-hfp**: `python -m mtspi.hfp_ag`. This is the Pi acting as the bike's *phone* (HFP Audio Gateway),
  written in-house because oFono offers the AG role only with a real SIM. It runs as a separate high-priority
  process for call audio. With the Carlinkit (`HFP_SOURCE=bridge`), the bridge connects to it over TCP
  `127.0.0.1:9160` (`--bike-audio`) and sends CarPlay audio and call state. hfp_ag carries them to the bike over
  A2DP and SCO.
- **mtspi-wifi-mode**: `system/wifi-mode.sh` switches wlan0 between "bike" mode and "home" mode. In bike mode, a
  dedicated `wpa_supplicant` (`mtspi-p2p`) handles Wi-Fi Direct and NetworkManager does not touch wlan0. Home
  mode uses NetworkManager. It also keeps the Bluetooth link to the bike up and the iPhone's oFono modem powered.
- **mtspi-setup**: `system/setup-file.sh` applies `mtspi.txt` from the boot partition at every boot (country,
  home Wi-Fi, SSH key, `SIRI=on|off` → `HFP_VR`).
- **mtspi-adapters**, **mtspi-btcentral**: set up the Bluetooth radio and keep the Pi central on every link.

### Inside the bridge (`mtspi/bridge.py`, the largest module)

- **Screen path:** Carlinkit USB (`carlinkit_usb.py` transport, `carlinkit.py` protocol, a Python port of
  node-CarPlay) → H.264 decoded with PyAV → redrawn at the dashboard's size (848×304) → JPEG → mySPIN session
  over Wi-Fi Direct (`session.py` + the binary `myspin/` package) → dashboard. Joystick events come back the same
  way, and `Display` maps them to CarPlay key codes (see below).
- **Screen modes:** `Display.mode` is either `"carplay"` or the Pi's own home screen. The home screen is drawn
  with PIL by `launcher.py`, `dashboard.py` and `testui.py`, and its strings come from `i18n.py` (en/it).
  `settings.py` holds the user settings and saves them atomically (tmp + fsync + replace), because the bike cuts
  power without warning.
- **Bluetooth services towards the bike:** `avrcp_bridge.py` (Music menu), `pbap.py`/`mns.py` (phonebook, recent
  calls, messages) and `bluez.py` (BlueZ, oFono and obexd over D-Bus with dbus-fast). The data comes from the
  iPhone's data-only Bluetooth link. The Pi deliberately offers no audio profile to the iPhone, so that all sound
  stays on CarPlay.
- **Calls and Siri:** the dongle reports calls through *audio commands* (phonecall_start/stop), not through a
  call-status message. bridge.py debounces these into call events for hfp_ag, which forwards them to the bike.
- `linkproto.py` is the frame format (u8 type + u32 LE length + data) of the "bikeaudio" link. The bridge uses it
  to reach both the emulated dashboard on the bench and hfp_ag on port 9160 on the Pi.
- `tasks.spawn()`: any fire-and-forget asyncio task **must** be started with it. The event loop holds only weak
  references, and a task that disappeared this way broke the bike's control channel on the bike.

### Bench vs Pi

`python -m mtspi.bridge` defaults to bench mode. In that mode the iPhone, the Carlinkit and the bike are TCP
endpoints of emulated programs (`--iphone 127.0.0.1:9172`, `--carlinkit 127.0.0.1:9175`, `--control tcp:9150`,
`--bt emulated`, `--wifi none`). `run.sh` passes the real-hardware values (`--bt real --control rfcomm --wifi
nmcli --carlinkit usb`). The emulated peers are not in this repository.

## Constraints and conventions

- `myspin/` is closed-source binary `.so` built for CPython 3.13 aarch64 and under a non-commercial licence. It
  cannot be edited or rebuilt here, and it does not import on a Mac. Code that imports `myspin` (session.py)
  runs only on the Pi.
- `install.sh` is shared by the manual install and the image build (`--image`, chroot, no live system). Any step
  that needs a running system must be wrapped in `live`. Do not let the two paths drift apart.
- Shell scripts are bash and must work on the Pi (GNU tools). `test_setup_file.sh` overrides paths through
  `MTSPI_*` env vars. Keep that hook when you change `setup-file.sh`.
- Code comments and test docstrings record *why*, often with the date and the on-bike or bench incident behind
  it. Keep that style. A behaviour fixed after a real incident usually has a regression test named after it
  (for example `test_bike_evening.py`).
- The README separates **bike** (tried on the real Multistrada) from **bench** (tried on the emulated
  dashboard). Never mark something as tried on the bike unless it was.
- Commit subjects are plain English sentences describing the change (for example "README: …", "Card image: …"),
  with no conventional-commit prefixes.

## Reverse-engineering research (branch `readocs`)

`REAdocs/` holds the mySPIN protocol research for an independent phone-side implementation (goal: an ESP32 showing
Hello World on the V4 S dashboard with joystick input). Before working on the protocol, the ESP32, or the test
platforms, read `REAdocs/memory/MEMORY.md` and the files it points to; the full write-up is
`REAdocs/myspin-protocol.md`, and `REAdocs/tools/run.sh` runs the analysis tools in an arm64 container. Update the
memory files when facts change. A `HANDOFF.md` at the repository root, if present, is the latest session handoff:
it is gitignored on purpose and must not be committed.
