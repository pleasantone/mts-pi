# Hidden state drops keys; vehicle value, locale, voice capabilities, a non-joystick DASH_CUSTOM, a soft button.
import struct
async def scenario(d):
    await d.setup()
    C = d.C
    d.send(C.Op.DASH_STATE, {"kind": 3, "value": 1, "screen": 0}); await d.sleep(0.1)
    d.key(31, 4, 2000); await d.sleep(0.1)          # dropped: phone screen hidden
    d.send(C.Op.DASH_STATE, {"kind": 3, "value": 0, "screen": 0}); await d.sleep(0.1)
    d.key(31, 4, 2100); await d.sleep(0.1)          # delivered
    d.send(C.Op.VEHICLE_VALUE, {"code": 2, "text": "12345", "extra": 0}); await d.sleep(0.1)
    d.send(C.Op.LOCALE, {"tag": b"ita"}); await d.sleep(0.1)
    d.send(C.Op.VOICE_CAPS, {"info": 1, "limits": 2}); await d.sleep(0.1)
    d.send_raw(67, [struct.pack("<BHH", 1, 1, 3), b"abc"]); await d.sleep(0.1)
    d.send(C.Op.SOFT_BUTTON, {"button": 12, "action": 4, "stamp": 77}); await d.sleep(0.2)
