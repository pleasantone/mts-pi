# REAdocs memory index

Repository-scope memory for the mySPIN reverse-engineering work. One fact per file; read the ones relevant to the task.

- [Project goal](project-goal.md) — ESP32 Hello World + joystick on the V4 S dashboard, and the path to it
- [Protocol facts](protocol-facts.md) — condensed wire facts: RFCOMM, JSON, UDP 8158, TCP header, frames, joystick
- [RE method](re-method.md) — arm64 container, constant recovery, fake peers, the `version` property gotcha
- [Open questions](open-questions.md) — what the real bike must still tell us, and how to find out
- [Platform decisions](platform-decisions.md) — Pi 4, Mac + Pi 4, original ESP32 with ESP-IDF + BTstack, Wi-Fi Direct levels
- [Repo workflow](repo-workflow.md) — fork/upstream remotes, `readocs` branch, handoff never committed
- [Working preferences](working-preferences.md) — plan and document before code; ask before executing
- [CarPlay side](carplay-side.md) — dongle-free wired ESP32-P4 (leaked key) vs the cheapest Carlinkit dongle; H.264 decode is the risk
