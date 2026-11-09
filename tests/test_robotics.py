"""Tests for ellmos-robotics MCP standard (ellmos.robotics.mcp.v1) and safety envelope."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from ellmos_robotics import (
    RoboticsHub,
    RoboticsSafetyEnvelope,
    RoboticsSafetyViolationError,
    default_estop_path,
)
from ellmos_robotics.cli import main


@pytest.fixture(autouse=True)
def isolate_estop_env(tmp_path, monkeypatch):
    """Ensure tests never mutate or read ~/.bach/robotics_estop.json by default (PB-13)."""
    dummy_estop = tmp_path / "isolated_estop.json"
    monkeypatch.setenv("BACH_ROBOTICS_ESTOP_PATH", str(dummy_estop))
    return dummy_estop


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


def test_estop_persists_across_hub_instances(tmp_path):
    state = tmp_path / "estop.json"
    RoboticsHub(state_path=state).robot_stop_emergency("hazard")
    fresh = RoboticsHub(state_path=state)  # new process / new request
    with pytest.raises(RoboticsSafetyViolationError, match="E-Stop active"):
        fresh.robot_actuate("gripper", 0.1)
    with pytest.raises(RoboticsSafetyViolationError, match="E-Stop active"):
        fresh.robot_navigate(0.1, 0.1)
    assert fresh.robot_telemetry()["emergency_stopped"] is True


def test_estop_reset_clears_persisted_state(tmp_path):
    state = tmp_path / "estop.json"
    RoboticsHub(state_path=state).robot_stop_emergency("hazard")
    hub = RoboticsHub(state_path=state)
    assert hub.reset_emergency_stop()["status"] == "e_stop_cleared"
    assert RoboticsHub(state_path=state).robot_actuate("gripper", 0.1)["status"] == "actuated"


def test_estop_reset_needs_permission(tmp_path):
    state = tmp_path / "estop.json"
    RoboticsHub(state_path=state).robot_stop_emergency("hazard")
    with pytest.raises(PermissionError):
        RoboticsHub(state_path=state, robotics_permission=False).reset_emergency_stop()
    with pytest.raises(RoboticsSafetyViolationError):
        RoboticsHub(state_path=state).robot_actuate("gripper", 0.1)


def test_estop_allowed_without_permission_and_persists(tmp_path):
    state = tmp_path / "estop.json"
    RoboticsHub(state_path=state, robotics_permission=False).robot_stop_emergency("hazard")
    with pytest.raises(RoboticsSafetyViolationError):
        RoboticsHub(state_path=state).robot_actuate("gripper", 0.1)


def test_unreadable_estop_state_fails_closed(tmp_path):
    state = tmp_path / "estop.json"
    state.write_text("{not json", encoding="utf-8")
    with pytest.raises(RoboticsSafetyViolationError, match="E-Stop active"):
        RoboticsHub(state_path=state).robot_actuate("gripper", 0.1)


def test_robotics_results_are_marked_demo():
    hub = RoboticsHub()
    assert hub.robot_capabilities()["demo"] is True
    assert hub.robot_telemetry()["demo"] is True
    assert hub.robot_actuate("gripper", 0.1)["demo"] is True
    assert hub.robot_navigate(0.1, 0.1)["demo"] is True
    assert hub.robot_stop_emergency()["demo"] is True


def test_default_shared_estop_path_respects_env_var(tmp_path, monkeypatch):
    custom_target = tmp_path / "custom_shared_estop.json"
    monkeypatch.setenv("BACH_ROBOTICS_ESTOP_PATH", str(custom_target))
    assert default_estop_path() == custom_target
    hub = RoboticsHub()
    assert hub.state_path == custom_target

    # Trigger E-Stop and verify it writes to custom_target
    hub.robot_stop_emergency("shared_test")
    assert custom_target.is_file()
    data = json.loads(custom_target.read_text(encoding="utf-8"))
    assert data["reason"] == "shared_test"

    # New Hub reads the same shared file
    fresh = RoboticsHub()
    assert fresh.robot_telemetry()["emergency_stopped"] is True


def test_default_shared_estop_path_falls_back_to_bach_home(monkeypatch):
    monkeypatch.delenv("BACH_ROBOTICS_ESTOP_PATH", raising=False)
    expected = Path.home() / ".bach" / "robotics_estop.json"
    assert default_estop_path() == expected
    hub = RoboticsHub()
    assert hub.state_path == expected


def test_cli_persists_to_shared_default_estop(tmp_path, monkeypatch, capsys):
    cli_target = tmp_path / "cli_estop.json"
    monkeypatch.setenv("BACH_ROBOTICS_ESTOP_PATH", str(cli_target))

    assert main(["estop", "--reason", "cli_hazard"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "emergency_stopped"
    assert out["persisted"] is True

    assert cli_target.is_file()
    saved = json.loads(cli_target.read_text(encoding="utf-8"))
    assert saved["reason"] == "cli_hazard"

    # Verify a new hub picks it up
    hub = RoboticsHub()
    assert hub.robot_telemetry()["emergency_stopped"] is True

