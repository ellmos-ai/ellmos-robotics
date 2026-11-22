---
name: Bug Report / Fehlerbericht
about: Report a safety-envelope bug, E-Stop issue, CLI error, or documentation mismatch
title: "[Bug] "
labels: ["bug"]
---

## Summary / Zusammenfassung
Describe the unexpected behavior concisely.

## Environment / Umgebung
- OS:
- Python version (`python --version`):
- `ellmos-robotics` version: `0.1.0`

## Steps to Reproduce / Schritte zur Reproduktion
1. Run command or Python snippet (use a temporary `--state-path`).
2. Observe output / exception.

## Expected Behavior / Erwartetes Verhalten
What should happen (e.g., `RoboticsSafetyViolationError` raised on E-Stop)?

## Checklist
- [ ] Tested with an isolated `--state-path` (not modifying production `~/.bach/robotics_estop.json`)
- [ ] Confirmed this is not a simulation-only stub limitation (`"demo": true`)
