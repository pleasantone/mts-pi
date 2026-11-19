---
name: project-goal
description: The user's goal for the mySPIN research: an ESP32 that shows Hello World on the Multistrada V4 S dashboard and reacts to the joystick
metadata:
  type: project
---

Goal (set 18 Nov 2026): write an application on an ESP32 that connects to the user's Multistrada V4 S, shows a
simple "Hello World" through the dashboard's mySPIN (Ducati Connect) screen, and demonstrates joystick input.

The path agreed so far: Pi 4 test platform with `mtspi/session.py` -> own Python implementation of each layer
(Mac + Pi 4 setup) -> port to an original ESP32. See [[platform-decisions]] and [[open-questions]].

**Why:** the closed `myspin/` binaries only run on Linux aarch64 with Python 3.13; an independent implementation is
needed for a microcontroller.
**How to apply:** frame new work as a step on that path; the full write-up is `REAdocs/myspin-protocol.md`.
