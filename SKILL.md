---
name: ellmos-robotics
version: 0.1.0
description: >
  Product skill for ellmos-robotics (standard ellmos.robotics.mcp.v1): dependency-free
  Python tool hub with safety envelope validation, fail-closed persistent E-Stop,
  permission gating, and simulation driver stubs (ROS 2, ESP32, LeRobot, MAVLink).
license: MIT
homepage: https://github.com/ellmos-ai/ellmos-robotics
---

# ellmos-robotics — Product Skill (P-022)

> **Product Skill for AI Agents & Operators** | Version: `0.1.0` | Runtime: Python `>=3.10` (zero runtime dependencies) | Status: **Simulation only (`"demo": true`)**

## 1. Purpose & Scope

Use `ellmos-robotics` when integrating or testing the canonical `ellmos.robotics.mcp.v1` tool surface, validating motion commands against `RoboticsSafetyEnvelope`, or exercising fail-closed persistent Emergency-Stop (`E-Stop`) workflows across CLI invocations and Python processes.

### What `ellmos-robotics` Does
- Exposes five core MCP-style tools plus reset on `RoboticsHub`:
  - `robot_capabilities()` — returns `schema`, `demo`, `drivers`, `joints`, `coordinate_frames`, and `safety_envelope`.
  - `robot_telemetry()` — returns simulated `position`, `joints`, `battery_pct`, `emergency_stopped`, `human_in_collision_zone`, and UTC `timestamp`.
  - `robot_actuate(joint_or_axis, target_value, *, speed_mps=0.2, force_n=5.0)` — validates joint name, E-Stop, collision zone, speed, and force before updating in-memory joint state.
  - `robot_navigate(x, y, z=0.25, *, speed_mps=0.25, frame_id="base_link")` — validates E-Stop, collision zone, speed, and 3D workspace bounds (`X/Y in [-2.0, 2.0]`, `Z in [0.0, 1.8]`) before updating position.
  - `robot_stop_emergency(reason="operator_e_stop")` — **always allowed**, even when `robotics_permission=False`; atomically persists E-Stop JSON via `.tmp` + `os.replace()`.
  - `reset_emergency_stop()` — requires `robotics_permission=True`; removes the persisted E-Stop file and clears in-memory stop flags.
- Enforces **fail-closed persistence**: any unreadable or malformed E-Stop JSON file counts as actively stopped (`estop_state_unreadable`).

### What `ellmos-robotics` Does NOT Do
- Does **not** communicate with physical hardware. `Ros2BridgeDriver`, `SerialEsp32Driver`, `LeRobotDriver`, and `MavlinkDroneDriver` are metadata stubs carrying `driver_id` and `protocol`.
- Does **not** replace physical safety relays or hardware emergency circuits. Every hub payload sets `"demo": true`.
- Does **not** implement the `ellmos-sensation` camera/sensor feed itself (it exposes the `human_in_collision_zone` flag on `RoboticsSafetyEnvelope`).

---

## 2. Installation & Prerequisites

- **Runtime:** Python `>=3.10` (stdlib only, zero third-party runtime dependencies)
- **Network egress:** `none` (100% local in-memory simulation + local JSON E-Stop file)

```bash
python -m venv .venv
# Windows:
.venv/Scripts/python -m pip install -e .
# Linux / macOS:
.venv/bin/python -m pip install -e .
```

Optional test dependencies:

```bash
pip install -e ".[dev]"   # pytest>=8.0
```

---

## 3. Safe Usage (CLI & Python API)

Always pass an explicit `--state-path` (or set `BACH_ROBOTICS_ESTOP_PATH`) during testing and automation so you do not mutate the user's shared `~/.bach/robotics_estop.json` file.

### CLI Commands (`ellmos-robotics`)

```bash
# Inspect capabilities and envelope defaults
ellmos-robotics --state-path ./estop.json capabilities

# Read simulated telemetry
ellmos-robotics --state-path ./estop.json telemetry

# Actuate a joint within safety bounds
ellmos-robotics --state-path ./estop.json actuate gripper 0.5 --speed 0.2 --force 5.0

# Navigate to a 3D waypoint within workspace bounds
ellmos-robotics --state-path ./estop.json navigate 0.5 0.5 0.25

# Trigger persistent fail-closed E-Stop (works without robotics_permission)
ellmos-robotics --state-path ./estop.json estop --reason "operator_check"
```

### Python API (`ellmos_robotics.mcp_standard`)

```python
from ellmos_robotics import (
    RoboticsHub,
    RoboticsSafetyEnvelope,
    RoboticsSafetyViolationError,
)

hub = RoboticsHub(state_path="./estop.json")
caps = hub.robot_capabilities()
res = hub.robot_actuate("gripper", 0.5, speed_mps=0.2, force_n=4.0)
stop = hub.robot_stop_emergency("manual_check")

# Clearing E-Stop requires robotics_permission=True
cleared = hub.reset_emergency_stop()
```

---

## 4. Boundaries, Permissions & Verification

| Operation | `robotics_permission=False` | Active E-Stop | `human_in_collision_zone=True` |
|---|---|---|---|
| `robot_capabilities()` | `PermissionError` | Allowed (reports `emergency_stopped: true`) | Allowed |
| `robot_telemetry()` | `PermissionError` | Allowed (reports `emergency_stopped: true`) | Allowed |
| `robot_actuate(...)` | `PermissionError` | `RoboticsSafetyViolationError` | `RoboticsSafetyViolationError` |
| `robot_navigate(...)` | `PermissionError` | `RoboticsSafetyViolationError` | `RoboticsSafetyViolationError` |
| `robot_stop_emergency(...)` | **Allowed** | Allowed (refreshes persisted stop) | **Allowed** |
| `reset_emergency_stop()` | `PermissionError` | Allowed (with permission) | Clears E-Stop only |

### Verification Readback

```bash
pytest -ra -v
ellmos-robotics --state-path ./tmp_estop.json capabilities
```

Verify that `"schema"` equals `"ellmos.robotics.mcp.v1"`, `"demo"` equals `true`, and `tests/test_robotics.py` passes completely before trusting any envelope behavior.
