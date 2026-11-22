---
name: Feature Request / Funktionswunsch
about: Propose a new driver adapter, safety envelope rule, or MCP tool extension
title: "[Feature] "
labels: ["enhancement"]
---

## Problem / Motivation
What robotics workflow, protocol adapter, or safety check is missing?

## Proposed Design / Vorgeschlagene Umsetzung
- Affected module (`mcp_standard.py`, `cli.py`, docs):
- Safety & fail-closed considerations:
- Backward compatibility with `ellmos.robotics.mcp.v1`:

## Checklist
- [ ] Preserves zero third-party runtime dependencies in core (or proposes optional extra)
- [ ] Keeps fail-closed E-Stop invariants intact
