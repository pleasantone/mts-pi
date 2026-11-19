# Every rider key and action as the phone decodes them; a key changes the screen, so the held FRAME_WANTED is answered.
# Codes: 30 UP, 31 DOWN, 32 LEFT, 33 RIGHT, 12 OK, 14 BACK, 20/21 ROTATE_CW/CCW.
# Actions: 1 PRESS, 2 RELEASE, 3 LONG_PRESS, 4 CLICK, 6 ABORT.
# The real V4 S: UP/DOWN as PRESS, LONG_PRESS (~0.9 s), RELEASE; LEFT/RIGHT/OK as CLICK only (README, 16 Nov 2026).
async def scenario(d):
    await d.setup()
    for code, action in [(30, 1), (30, 3), (30, 2), (31, 4), (32, 4), (33, 4), (12, 4), (14, 4), (20, 4), (21, 4)]:
        d.key(code, action, 1000)
        await d.sleep(0.15)
