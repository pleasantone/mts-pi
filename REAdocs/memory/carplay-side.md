---
name: carplay-side
description: The CarPlay-input half of the project — dongle-free wired ESP32-P4 (leaked MFi key) preferred, Carlinkit dongle as the wireless alternative, H.264 decode is the one hard step
metadata:
  type: project
---

Decision (19 Nov 2026) on the second processor that feeds CarPlay frames to the mySPIN ESP32. Full write-up:
`REAdocs/myspin-protocol.md`, section "The CarPlay side". A second chip is needed because CarPlay wants USB host
+ H.264 decode while mySPIN wants Bluetooth Classic + Wi-Fi Direct; no one ESP32 has all four. The two are linked
by SPI (JPEG frames out, joystick in).

- **Design A, preferred (dongle-free, wired):** iPhone -> ESP32-P4 over USB (wired CarPlay = whole iAP2 + AirPlay
  session over the cable, no BT/Wi-Fi, no dongle, no radio co-processor). Software MFi signer with a LEAKED key.
  P4 decodes H.264 in software, encodes 848x304 JPEG in hardware. Start from CarPlay-Tab5
  (github.com/sky18Dragon/CarPlay-Tab5): exactly this, tested iOS 16 and 26, GPL-3.0. Two bare boards ~$10-20 each.
- **Design B (wireless alt):** cheapest Carlinkit CPC200-CCPA (~$27-30 AliExpress/Alibaba, vs ~$65 official) does
  the radios + genuine MFi chip; the P4 or the original ESP32 reads its USB protocol, already in the repo
  (`mtspi/carlinkit.py`, node-CarPlay port). Must be the CPC200-CCPA: repo only knows USB IDs 1314:1520/1521.
- **Codec:** CarPlay is H.264 only (HEVC optional, harder). No JPEG/raw mode, and the bike wants JPEG, so the
  decode+re-encode transcode is unavoidable. Decode is the one expensive step (P4 has no HW H.264 decoder: software
  OpenH264, ~16 fps at 890x240 reported). JPEG encode is free (P4 hardware). Lever = small frame + low fps; bike
  only shows 7-13 fps. If decode is too slow, use a chip with HW H.264 decode (Pi Zero 2 W), not another codec.
- **Screen size:** CarPlay is TOLD the resolution (`send_open(width,height,fps)`, default 848x304); README: "asked
  for exactly that size. Nothing is scaled, and there are no black bands." Even dimensions; real dashboard size.
- **The number that decides Design A:** P4 software H.264 decode fps at 848x304. Measure first.

**Leaked-key caveat:** the MFi key is extracted from Carlinkit/DiPlay firmware, never issued to this project; Apple
can revoke it, iOS updates may break it. Educational/private only; never distribute. Design B avoids it.

Related: [[platform-decisions]], [[project-goal]].
