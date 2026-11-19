---
name: project-goal
description: Two tracks — Track 1 (primary) is a standalone ESP32 mySPIN Hello World + joystick on the V4 S dashboard; Track 2 (optional, larger) feeds real iPhone CarPlay to the bike
metadata:
  type: project
---

Two separate projects; keep them apart. **Track 1 is the core goal**, Track 2 is an optional later expansion.
The user reaffirmed (19 Nov 2026) that the standalone ESP32-only Hello World "may be more relevant than the
CarPlay discussion". Full write-up: `REAdocs/myspin-protocol.md`, "Recommended build".

**Track 1 — standalone mySPIN Hello World (primary).** One original ESP32, NO iPhone and NO CarPlay. It joins the
bike over Bluetooth + Wi-Fi Direct and draws its own 848x304 screen on the dashboard, moved by the joystick.
Cheapest build (one ~$6-10 ESP32-WROVER-E), stands alone, needs nothing from the CarPlay work. Everything it needs
is the mySPIN protocol + the ESP32 plan. The one risk is the Wi-Fi Direct join from an ESP32 ([[open-questions]]). A reference implementation of the Track 1 capstone exists: `REAdocs/tools/paddle_game.py` (a joystick paddle game as a mySPIN frames object) runs through the fake dashboard (`fake_dashboard.py --game`), demo at `REAdocs/tools/paddle-demo.gif`. Doom is a documented stretch (doomgeneric fits the same frames interface; best on an ESP32-P4 frame source; see the protocol doc "Beyond Hello World: Doom").

**Track 2 — feed real CarPlay to the bike (optional).** Only if the iPhone's actual CarPlay is wanted on the
dashboard. Adds MFi auth + H.264 decode; a Raspberry Pi earns its place over an ESP32 here. See [[carplay-side]]
and [[platform-decisions]] for the dongle/chip/Pi cost analysis.

**Development path (both tracks):** Pi 4 test platform with `mtspi/session.py` -> own Python implementation of each
layer (Mac + Pi 4) -> port to an original ESP32. Recommended: do Track 1 on an ESP32 first; develop Track 2 on a
Pi Zero 2 W and only shrink to ESP32 later.

**Why:** the closed `myspin/` binaries only run on Linux aarch64 with Python 3.13; an independent implementation is
needed for a microcontroller.
