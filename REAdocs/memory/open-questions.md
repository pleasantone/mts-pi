---
name: open-questions
description: Facts about the real V4 S still unknown as of 18 Nov 2026 and the log line or test that answers each
metadata:
  type: project
---

Unknown as of 18 Nov 2026 (nothing has been run on the bike in this research):

1. Protocol revision in the dashboard HELLO (1.1/1.2/2.0) -> Pi log `hello_received`.
2. `coding_mask`, pixel format, byte order -> Pi log `display_described`.
3. Real announcement address/port/identification -> first UDP 8158 datagram, or Pi log `tcp_connected`.
4. Does the group passphrase survive key-off? -> capture it (sha256 fingerprints only) across key-ons.
5. Does the group owner accept a legacy (non-P2P) WPS-PIN client? -> Pi experiment: plain wpa_supplicant,
   `wpa_cli wps_pin <bssid> <pin>`. Decides the ESP32 Wi-Fi level ([[platform-decisions]]).
6. Which optional phone messages the dashboard requires (time customs, launcher state, SUBSCRIBE, BT-profile text).
7. Band of the bike's group (2.4 or 5 GHz) -> `wpa_cli -p /run/wpa_p2p status` (`freq=`). 5 GHz rules out ESP32.

**How to apply:** when a bike session happens, update this file and the Open questions table in
`REAdocs/myspin-protocol.md`.
