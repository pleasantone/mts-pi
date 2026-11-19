---
name: repo-workflow
description: Git remotes, branches and what is committed for the mySPIN research (fork pleasantone/mts-pi, readocs branch, handoff not committed)
metadata:
  type: project
---

- `origin` = the user's fork `pleasantone/mts-pi` (public; GitHub keeps forks of public repos public).
  `upstream` = `nostoi-labs/mts-pi`. Local `main` tracks `origin/main`.
- Fork `main` mirrors upstream; keep it fast-forwardable: `gh repo sync pleasantone/mts-pi --source nostoi-labs/mts-pi`.
- Research lives on branch `readocs` (REAdocs/, CLAUDE.md, ignore rules). The user chose to publish the full
  protocol write-up on the public fork.
- Handoff notes (`HANDOFF*.md`) are temporary and gitignored; never commit them.
- Commit subjects: plain English sentences, no conventional-commit prefixes (CLAUDE.md).
