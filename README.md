<p align="center">
  <img src="assets/banner.svg" alt="ellmos-robotics banner" width="100%">
</p>

# ellmos-robotics

**English** | [Deutsch](README_de.md)

Tool standard `ellmos.robotics.mcp.v1` for LLM-to-robot communication in the ellmos ecosystem (BACH, Open Ocean): a hub with five robot tools, a safety envelope (speed, force, workspace bounds, E-Stop) and driver profiles. A small, dependency-free Python package.

> **Status: early (v0.1.0), simulation only.** The driver classes (`ros2_bridge`, `serial_esp32`, `lerobot_embodied`, `mavlink_rover`) are stubs that carry an id and a protocol name; none of them talks to hardware. All hub results come from simulated in-memory state and are marked `"demo": true`. The safety logic (envelope checks, persistent E-Stop) is real and tested, but this package must not be used to move physical hardware as is.

## What it does

- **`RoboticsHub`** implements the tool surface:
  - `robot_capabilities()`: drivers, joints (`shoulder_pan`, `elbow_flex`, `wrist_roll`, `gripper`), coordinate frames, current safety envelope
  - `robot_telemetry()`: simulated position, joint values, battery, E-Stop and collision-zone flags, timestamp
  - `robot_actuate(joint, value, speed_mps=0.2, force_n=5.0)`
  - `robot_navigate(x, y, z=0.25, speed_mps=0.25, frame_id="base_link")`
  - `robot_stop_emergency(reason)`: always allowed, even without robotics permission
  - `reset_emergency_stop()`: requires robotics permission
- **`RoboticsSafetyEnvelope`** (defaults): max speed 0.5 m/s, max force 15 N, workspace x and y in [-2, 2], z in [0, 1.8]. A request is rejected with `RoboticsSafetyViolationError` when the E-Stop is active, when `human_in_collision_zone` is set, when speed or force is too high, or when a waypoint is outside the bounds.
- **Persistent E-Stop (fail-closed):** the stop is written atomically to a state file and adopted by every new hub instance. An unreadable or malformed state file counts as stopped. Default path is `~/.bach/robotics_estop.json`, overridable with the environment variable `BACH_ROBOTICS_ESTOP_PATH`, the `state_path` argument or the CLI option `--state-path`.
- **Permission gate:** with `robotics_permission=False` all tools except the E-Stop raise `PermissionError`.

## Installation

Requires Python 3.10 or newer; there are no runtime dependencies. From a clone:

```bash
pip install -e .
pip install -e ".[dev]"   # pytest
```

## Usage

```bash
ellmos-robotics capabilities
ellmos-robotics telemetry
ellmos-robotics actuate gripper 0.5 --speed 0.2 --force 5
ellmos-robotics navigate 0.5 0.5 0.25
ellmos-robotics --state-path ./estop.json estop --reason "test"
ellmos-robotics --state-path ./estop.json telemetry
```

```python
from ellmos_robotics.mcp_standard import RoboticsHub

hub = RoboticsHub(state_path="estop.json")
hub.robot_navigate(0.5, 0.5)
hub.robot_stop_emergency("operator")
# any later robot_actuate / robot_navigate now raises RoboticsSafetyViolationError
```

Note that the CLI `estop` command writes the shared E-Stop file; reset it from Python with `reset_emergency_stop()` or by deleting the state file. Tests live in `tests/test_robotics.py` (run with `pytest`).

## Relation to ellmos and Open Ocean

`ellmos-robotics` is one of the extension modules listed in the [Open Ocean](https://github.com/ellmos-ai/open-ocean) module map. The envelope has a `human_in_collision_zone` flag intended to be fed by [ellmos-sensation](https://github.com/ellmos-ai/ellmos-sensation); that coupling is not implemented in this repository. Module metadata is in `ellmos-module.v2.json`.

## License

MIT, as declared in `pyproject.toml`.
