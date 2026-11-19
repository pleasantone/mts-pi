"""A paddle-and-ball game as a mySPIN `frames` object (reference for Track 1, the standalone ESP32 build).

It is an original game in the paddle-and-ball genre, not a reproduction of any specific branded title. The point is
that the mySPIN session already gives you a game-loop interface, so the game is small:

    version        a property the feed polls; bump it and the dashboard pulls a new frame
    render(w, h)    draw the current state into a (w x h) image
    on_key(k, a)    joystick input: UP/DOWN hold to move, OK to serve
    tick()          advance the physics one step and bump version  <-- the one thing a static Hello World lacks

The same four pieces map straight onto the ESP32: render into a framebuffer, an on_key callback, and a ~15 Hz
FreeRTOS timer calling tick(). Scores use a tiny 3x5 block font so there is no font-library dependency, exactly as
on the ESP32. Nothing here needs CarPlay, the iPhone or a dongle.
"""
from __future__ import annotations

import random

from PIL import Image, ImageDraw

# 3x5 block digits: one filled cell per '1'. No font file needed (the ESP32 has none either).
_FONT3x5 = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
}


class PaddleGame:
    def __init__(self, width=848, height=304, auto_player=False, seed=1):
        self.W, self.H = width, height
        self.auto_player = auto_player          # True = both paddles driven by the computer (for demos/GIFs)
        self.rng = random.Random(seed)
        self.paddle_w, self.paddle_h = 12, 56
        self.ball = 12                          # ball side length
        self.margin = 20                        # paddle distance from the side wall
        self.player_speed = 12                  # how fast the human paddle moves while a key is held
        self.ai_speed = 7                       # computer paddle cap (< ball reach, so it is beatable)
        self.ball_speed = 20
        self.py = (self.H - self.paddle_h) / 2  # left paddle (the human)
        self.cy = (self.H - self.paddle_h) / 2  # right paddle (the computer)
        self.score = [0, 0]                     # [left/human, right/computer]
        self.player_dir = 0                     # -1 up, +1 down, 0 stop (set by on_key)
        self._version = 0
        self.frames_sent = 0
        self._serve(to_right=True)

    # --- the mySPIN frames interface -------------------------------------------------
    @property
    def version(self):
        return (self._version,)

    def on_key(self, key, action):
        # Real V4 S: UP/DOWN arrive as PRESS -> (LONG_PRESS) -> RELEASE; others as CLICK only. So hold to move.
        if self.auto_player:
            return
        if key in ("UP", "DOWN"):
            if action == "PRESS":
                self.player_dir = -1 if key == "UP" else 1
            elif action in ("RELEASE", "ABORT"):
                self.player_dir = 0
            # LONG_PRESS is ignored: keep moving while held
        elif key == "OK" and action in ("CLICK", "PRESS"):
            pass  # reserved: serve/pause; the ball serves itself after a point here

    def on_frame_sent(self, size):
        self.frames_sent += 1

    # --- game logic ------------------------------------------------------------------
    def _serve(self, to_right):
        self.bx = (self.W - self.ball) / 2
        self.by = (self.H - self.ball) / 2
        angle = self.rng.uniform(-0.6, 0.6)
        self.vx = self.ball_speed * (1 if to_right else -1)
        self.vy = self.ball_speed * angle

    def _track(self, paddle_y, cap, imperfect):
        # Move a computer paddle toward the ball, capped (so it can lose). `imperfect` adds a little aim error.
        target = self.by + self.ball / 2 - self.paddle_h / 2
        if imperfect:
            target += self.rng.uniform(-22, 22)
        delta = target - paddle_y
        step = max(-cap, min(cap, delta))
        return paddle_y + step

    def _drift(self, paddle_y):
        # When the ball is in the far half, ease back toward center (and so occasionally arrive late = a miss).
        target = (self.H - self.paddle_h) / 2
        return paddle_y + max(-4, min(4, target - paddle_y))

    def tick(self):
        # Left paddle: the human (player_dir), or in demo mode an imperfect computer that only acts in its own half.
        if self.auto_player:
            if self.bx < self.W * 0.5:
                self.py = self._track(self.py, self.player_speed - 3, imperfect=True)
            else:
                self.py = self._drift(self.py)
        else:
            self.py += self.player_dir * self.player_speed
        self.py = max(0, min(self.H - self.paddle_h, self.py))

        # Right paddle: the computer, reacting only once the ball is in its half (a short reaction window = misses).
        if self.vx > 0 and self.bx > self.W * 0.5:
            self.cy = self._track(self.cy, self.ai_speed, imperfect=True)
        else:
            self.cy = self._drift(self.cy)
        self.cy = max(0, min(self.H - self.paddle_h, self.cy))

        # Ball.
        self.bx += self.vx
        self.by += self.vy
        if self.by <= 0:
            self.by = 0
            self.vy = abs(self.vy)
        elif self.by >= self.H - self.ball:
            self.by = self.H - self.ball
            self.vy = -abs(self.vy)

        lx = self.margin + self.paddle_w
        rx = self.W - self.margin - self.paddle_w
        # Left paddle hit
        if self.vx < 0 and self.bx <= lx and self.py - self.ball <= self.by <= self.py + self.paddle_h:
            self.bx = lx
            self._bounce(self.py)
        # Right paddle hit
        elif self.vx > 0 and self.bx + self.ball >= rx and self.cy - self.ball <= self.by <= self.cy + self.paddle_h:
            self.bx = rx - self.ball
            self._bounce(self.cy)
        # Missed: score and re-serve toward whoever was scored on
        elif self.bx < -self.ball:
            self.score[1] += 1
            self._serve(to_right=False)
        elif self.bx > self.W:
            self.score[0] += 1
            self._serve(to_right=True)

        self._version += 1     # tell the feed the screen changed

    def _bounce(self, paddle_y):
        # Reverse x and add spin from where the ball met the paddle; keep a real vertical component so rallies are
        # not a flat line, and speed up a little each hit (capped) so a paddle eventually cannot keep up.
        import math
        hit = max(-1.0, min(1.0, (self.by + self.ball / 2 - (paddle_y + self.paddle_h / 2)) / (self.paddle_h / 2)))
        speed = min(self.ball_speed * 1.5, math.hypot(self.vx, self.vy) + 0.8)
        direction = -1 if self.vx > 0 else 1
        ang = hit * 1.15
        vy = speed * math.sin(ang)
        if abs(vy) < 4.0:
            vy = 4.0 if hit >= 0 else -4.0
        self.vx = direction * max(6.0, abs(speed * math.cos(ang)))
        self.vy = vy

    # --- drawing ---------------------------------------------------------------------
    def _digit(self, d, x, y, s, draw, fill):
        for row, bits in enumerate(_FONT3x5[d]):
            for col, b in enumerate(bits):
                if b == "1":
                    draw.rectangle([x + col * s, y + row * s, x + col * s + s - 1, y + row * s + s - 1], fill=fill)

    def _number(self, n, cx, y, s, draw, fill):
        text = str(n)
        w = len(text) * (3 * s + s) - s
        x = cx - w / 2
        for ch in text:
            self._digit(ch, x, y, s, draw, fill)
            x += 3 * s + s

    def render(self, w, h):
        img = Image.new("RGB", (w, h), (0, 0, 0))
        d = ImageDraw.Draw(img)
        white = (235, 235, 235)
        # center net (dashed)
        for yy in range(6, h, 24):
            d.rectangle([w / 2 - 2, yy, w / 2 + 1, yy + 12], fill=(90, 90, 90))
        # scores
        s = 7
        self._number(self.score[0], w * 0.5 - 60, 14, s, d, white)
        self._number(self.score[1], w * 0.5 + 60, 14, s, d, white)
        # paddles
        d.rectangle([self.margin, self.py, self.margin + self.paddle_w, self.py + self.paddle_h], fill=white)
        d.rectangle([w - self.margin - self.paddle_w, self.cy, w - self.margin, self.cy + self.paddle_h], fill=white)
        # ball
        d.rectangle([self.bx, self.by, self.bx + self.ball, self.by + self.ball], fill=white)
        return img
