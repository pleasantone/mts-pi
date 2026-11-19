---
name: platform-decisions
description: Agreed test and target platforms (Pi 4 only, Mac + Pi 4 over Ethernet, original ESP32 with ESP-IDF + BTstack) and the Wi-Fi Direct strategy
metadata:
  type: project
---

Decisions of 18 Nov 2026:

- **Test platform: Raspberry Pi 4** (the only Pi available; MTS Pi was tried on the bike only with a Pi 3 A+, same
  CYW43455 radio). Fresh Raspberry Pi OS Lite 64-bit + `./install.sh --no-carlinkit`; run `mtspi/session.py`
  instead of the bridge. Power from a power bank (Pi 4 wants 3 A, tank socket gives 1 A).
- **Mac + Pi 4:** Mac cannot join alone (no Wi-Fi Direct/WPS API). Pi does Bluetooth + Wi-Fi Direct and NATs the
  Mac's TCP session over Ethernet. Needs a `--radio-only` mode in `session.py` that does not exist yet.
- **ESP32:** original ESP32 only (S2/S3/C3/C6 lack Bluetooth Classic), WROVER-E with PSRAM, ESP-IDF 5.x (not
  Arduino), BTstack preferred over Bluedroid (custom SDP UUID + channel 22). Pictures = precomputed baseline JPEGs.
- **CarPlay side (second processor):** separate chip, see [[carplay-side]]. Preferred: dongle-free wired ESP32-P4
  with a leaked MFi key (Design A). Alternative: cheapest Carlinkit CPC200-CCPA for wireless (Design B).
- **Wi-Fi Direct on ESP32:** level 1 legacy WPS-PIN join (days) first; level 2 P2P IE + provision discovery via
  `esp_wifi_set_vendor_ie` / `esp_wifi_80211_tx` only if needed; full Wi-Fi Direct not needed. Settle with the Pi
  experiment in [[open-questions]] first.

**Why:** chosen with the user while writing `REAdocs/myspin-protocol.md`; all untested on hardware.

**Recommended build (19 Nov 2026), from the cost analysis in [[carplay-side]]:**
- Track 1 (standalone mySPIN Hello World): one original ESP32-WROVER-E, ~$6-10. No iPhone/dongle/chip. See [[project-goal]].
- Track 2 wireless (most proven, = MTS Pi): Pi Zero 2 W + Carlinkit CPC200-CCPA + OTG adapter, ~$45; dongle's genuine chip.
- Track 2 wired, cheapest: Pi Zero 2 W + powered USB splitter, ~$20-30; leaked software key.
- Track 2 wired, robust: Pi Zero 2 W + MFI343S00177 + breakout + CH341A, ~$35-45; genuine chip (Design A+).
- Pi Zero 2 W: $15 list, ~$18-24 from resellers (often sold out).
- Rationale: wireless needs the iPhone's own radios (-> dongle); wired puts the iPhone on USB and frees the board's
  radio for the bike (-> no dongle). A Pi has hardware H.264 decode (the ESP32-P4's weak spot) and runs the mySPIN
  code already. Develop Track 2 on the Pi; the two-ESP32 (P4 + original) design is the end-goal shrink, not the dev platform.
