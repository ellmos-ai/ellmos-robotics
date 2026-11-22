# Security Policy / Sicherheitsrichtlinie

## Simulation & Physical Safety Notice

> **IMPORTANT:** `ellmos-robotics` (`v0.1.0`) is an **early simulation-only reference implementation** (`"demo": true`). The driver classes (`ros2_bridge`, `serial_esp32`, `lerobot_embodied`, `mavlink_rover`) are stubs and do not control physical hardware. **Do not deploy this package as a sole safety mechanism for physical robots or actuators.**

## Security Guarantees in Scope

- **Fail-Closed E-Stop Persistence:** Corrupted, malformed, or unreadable `robotics_estop.json` files must always evaluate as `emergency_stopped = True`.
- **Unprivileged Emergency Stop:** `robot_stop_emergency()` bypasses `robotics_permission=False` so an emergency stop can never be blocked by a permission gate.
- **Permission-Gated Reset & Motion:** `reset_emergency_stop()`, `robot_actuate()`, `robot_navigate()`, `robot_capabilities()`, and `robot_telemetry()` require `robotics_permission=True`.
- **Zero Network Egress:** The core package performs no network requests and requires no external runtime dependencies.

## Reporting a Vulnerability

Please **do not** open public GitHub issues for security or safety-bypass vulnerabilities (e.g., E-Stop bypasses, path traversal in state files, or envelope validation flaws).

- Preferred channel: [GitHub Private Vulnerability Reporting](https://github.com/ellmos-ai/ellmos-robotics/security/advisories/new)
- Email fallback: `security@open-bricks.org`
- Target initial response SLA: within **48 hours**.

## Statutory Notice (§ 521 BGB)

This software is provided free of charge under the [MIT License](LICENSE). Liability for gratis software is governed by the MIT License terms and, where applicable under German law, § 521 BGB (intent and gross negligence only).
