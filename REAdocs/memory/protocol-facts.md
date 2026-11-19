---
name: protocol-facts
description: Condensed mySPIN wire facts for the V4 S (RFCOMM service, control JSON, UDP 8158, TCP header, handshake, frames, joystick, keep-alive)
metadata:
  type: reference
---

Full detail: `REAdocs/myspin-protocol.md`. Phone side observed, dashboard side inferred ([[re-method]]).

- **Bluetooth:** phone publishes SDP `MySpinBluetooth`, UUID `31fd954e-8138-4367-a201-0276b9716fb1`, RFCOMM
  channel 22; the bike is the client. Newline-terminated JSON `{"id":uuid4,"type":...,"payload":{...}}`, control
  revision 3. Phone: phoneDetectRequest -> phoneInitRequest -> phoneWlanStateRequest -> phoneWlanP2PPinConnectionRequest;
  bike answers iviInitResponse (connectionType P2P/AP, authenticationType PIN/PBC), then deviceName + pin.
- **Wi-Fi:** V4 S = persistent Wi-Fi Direct group owner `DIRECT-..-p2p-mw-myspin`, joined with WPS PIN (keypad).
- **Discovery:** UDP broadcast to port 8158, JSON with `hostname` (or `hostname_v6`), `port`, `version` (int),
  `identification`. Phone then connects TCP.
- **TCP header:** u8 opcode, u32 reserved (0), u32 body length, little-endian. Dashboard speaks first (HELLO).
- **Setup (1.2):** HELLO->HELLO_OK; DISPLAY_INFO->DISPLAY_OK+IDENTITY+PHONE_READY; DASH_READY->(time customs,
  PHONE_STATE 4/1, SUBSCRIBE); PIXEL_SET->PIXEL_OK; CODING_SET->CODING_OK; FRAME_WANTED->FRAME.
- **Frames:** 848x304 on the V4 S; coding 1 JPEG, 2 zlib, 4 raw. Incremental requests are held until the screen
  changes. One request outstanding.
- **Joystick:** DASH_CUSTOM (67) kind 5, `code` = action (1 PRESS, 2 RELEASE, 3 LONG_PRESS, 4 CLICK, 6 ABORT),
  data = key u8 (30 UP, 31 DOWN, 32 LEFT, 33 RIGHT, 12 OK, 14 BACK, 20/21 rotate) + u32 ms. Real V4 S: UP/DOWN
  press/long/release, others CLICK only. DASH_STATE kind 3 value 1 = phone screen hidden, keys dropped.
- **Keep-alive:** PING every 2 s, PONG echoes; phone drops the session after 15 s without a dashboard packet.
