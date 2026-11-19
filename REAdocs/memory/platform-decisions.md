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
- **Wi-Fi Direct on ESP32:** level 1 legacy WPS-PIN join (days) first; level 2 P2P IE + provision discovery via
  `esp_wifi_set_vendor_ie` / `esp_wifi_80211_tx` only if needed; full Wi-Fi Direct not needed. Settle with the Pi
  experiment in [[open-questions]] first.

**Why:** chosen with the user while writing `REAdocs/myspin-protocol.md`; all untested on hardware.
