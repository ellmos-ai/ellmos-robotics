"""Tests for ellmos-robotics MCP standard (ellmos.robotics.mcp.v1) and safety envelope."""

from __future__ import annotations

import json
import pytest

from ellmos_robotics import (
    RoboticsHub,
    RoboticsSafetyEnvelope,
    RoboticsSafetyViolationError,
)
from ellmos_robotics.cli import main


def test_capabilities_and_telemetry():
    hub = RoboticsHub()
    caps = hub.robot_capabilities()
    assert caps["schema"] == "ellmos.robotics.mcp.v1"
    assert "ros2_bridge" in caps["drivers"]
    assert "lerobot_embodied" in caps["drivers"]
    tel = hub.robot_telemetry()
    assert tel["emergency_stopped"] is False


def test_actuation_and_navigation_within_bounds():
    hub = RoboticsHub()
    act = hub.robot_actuate("gripper", 0.75, speed_mps=0.2, force_n=4.0)
    assert act["status"] == "actuated"
    nav = hub.robot_navigate(0.5, -0.4, 0.3)
    assert nav["position"]["x"] == 0.5


def test_safety_envelope_blocks_excessive_speed_force_bounds_and_estop():
    hub = RoboticsHub()
    with pytest.raises(RoboticsSafetyViolationError, match="max_speed_mps"):
        hub.robot_actuate("shoulder_pan", 1.0, speed_mps=2.5)
    with pytest.raises(RoboticsSafetyViolationError, match="max_force_n"):
        hub.robot_actuate("gripper", 1.0, force_n=50.0)
    with pytest.raises(RoboticsSafetyViolationError, match="outside bounds"):
        hub.robot_navigate(10.0, 0.0, 0.25)

    hub.robot_stop_emergency("test_hazard")
    with pytest.raises(RoboticsSafetyViolationError, match="E-Stop active"):
        hub.robot_actuate("gripper", 0.1)


def test_sensation_collision_guard_blocks_motion():
    env = RoboticsSafetyEnvelope(human_in_collision_zone=True)
    hub = RoboticsHub(envelope=env)
    with pytest.raises(RoboticsSafetyViolationError, match="Human detected in collision zone"):
        hub.robot_navigate(0.1, 0.1, 0.25)


def test_cli_capabilities(capsys):
    assert main(["capabilities"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["schema"] == "ellmos.robotics.mcp.v1"
