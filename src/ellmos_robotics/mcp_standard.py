"""Canonical MCP Standard `ellmos.robotics.mcp.v1`, Drivers, and Safety Envelope."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


class RoboticsSafetyViolationError(PermissionError):
    """Raised when a robotics actuation or navigation violates the safety envelope or E-Stop."""


@dataclass
class RoboticsSafetyEnvelope:
    max_speed_mps: float = 0.5
    max_force_n: float = 15.0
    bounds_x: tuple[float, float] = (-2.0, 2.0)
    bounds_y: tuple[float, float] = (-2.0, 2.0)
    bounds_z: tuple[float, float] = (0.0, 1.8)
    emergency_stopped: bool = False
    emergency_reason: str | None = None
    human_in_collision_zone: bool = False

    def validate_actuation(self, speed_mps: float, force_n: float) -> None:
        if self.emergency_stopped:
            raise RoboticsSafetyViolationError(
                f"E-Stop active ({self.emergency_reason or 'manual'}); reset required before actuation."
            )
        if self.human_in_collision_zone:
            raise RoboticsSafetyViolationError(
                "Human detected in collision zone (ellmos-sensation guard); actuation blocked."
            )
        if speed_mps > self.max_speed_mps:
            raise RoboticsSafetyViolationError(
                f"Requested speed {speed_mps} m/s exceeds max_speed_mps ({self.max_speed_mps} m/s)."
            )
        if force_n > self.max_force_n:
            raise RoboticsSafetyViolationError(
                f"Requested force {force_n} N exceeds max_force_n ({self.max_force_n} N)."
            )

    def validate_waypoint(self, x: float, y: float, z: float, speed_mps: float) -> None:
        self.validate_actuation(speed_mps=speed_mps, force_n=0.0)
        if not (self.bounds_x[0] <= x <= self.bounds_x[1]):
            raise RoboticsSafetyViolationError(f"Waypoint X={x} outside bounds {self.bounds_x}")
        if not (self.bounds_y[0] <= y <= self.bounds_y[1]):
            raise RoboticsSafetyViolationError(f"Waypoint Y={y} outside bounds {self.bounds_y}")
        if not (self.bounds_z[0] <= z <= self.bounds_z[1]):
            raise RoboticsSafetyViolationError(f"Waypoint Z={z} outside bounds {self.bounds_z}")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class Ros2BridgeDriver:
    driver_id = "ros2_bridge"
    protocol = "rosbridge_v2_websocket"


class SerialEsp32Driver:
    driver_id = "serial_esp32"
    protocol = "json_rpc_uart_wifi"


class LeRobotDriver:
    driver_id = "lerobot_embodied"
    protocol = "lerobot_so100_aloha"


class MavlinkDroneDriver:
    driver_id = "mavlink_rover"
    protocol = "mavlink_v2_udp"


class RoboticsHub:
    """Implementation of the canonical `ellmos.robotics.mcp.v1` tool surface."""

    SCHEMA = "ellmos.robotics.mcp.v1"

    def __init__(
        self,
        envelope: RoboticsSafetyEnvelope | None = None,
        *,
        robotics_permission: bool = True,
    ):
        self.envelope = envelope or RoboticsSafetyEnvelope()
        self.robotics_permission = robotics_permission
        self.drivers = {
            Ros2BridgeDriver.driver_id: Ros2BridgeDriver(),
            SerialEsp32Driver.driver_id: SerialEsp32Driver(),
            LeRobotDriver.driver_id: LeRobotDriver(),
            MavlinkDroneDriver.driver_id: MavlinkDroneDriver(),
        }
        self._position = {"x": 0.0, "y": 0.0, "z": 0.25, "frame_id": "base_link"}
        self._joints = {"shoulder_pan": 0.0, "elbow_flex": 0.0, "wrist_roll": 0.0, "gripper": 0.0}
        self._battery_pct = 94.0

    def _require_permission(self) -> None:
        if not self.robotics_permission:
            raise PermissionError("Robotics control is disabled in Permissions (smarthome_robotics=False).")

    def robot_capabilities(self) -> dict[str, Any]:
        self._require_permission()
        return {
            "schema": self.SCHEMA,
            "drivers": sorted(self.drivers.keys()),
            "joints": sorted(self._joints.keys()),
            "coordinate_frames": ["base_link", "map", "end_effector"],
            "safety_envelope": self.envelope.as_dict(),
        }

    def robot_telemetry(self) -> dict[str, Any]:
        self._require_permission()
        return {
            "schema": self.SCHEMA,
            "position": dict(self._position),
            "joints": dict(self._joints),
            "battery_pct": self._battery_pct,
            "emergency_stopped": self.envelope.emergency_stopped,
            "human_in_collision_zone": self.envelope.human_in_collision_zone,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def robot_actuate(
        self,
        joint_or_axis: str,
        target_value: float,
        *,
        speed_mps: float = 0.2,
        force_n: float = 5.0,
    ) -> dict[str, Any]:
        self._require_permission()
        if joint_or_axis not in self._joints:
            raise KeyError(f"Unknown joint_or_axis: {joint_or_axis}")
        self.envelope.validate_actuation(speed_mps=speed_mps, force_n=force_n)
        self._joints[joint_or_axis] = float(target_value)
        return {
            "schema": self.SCHEMA,
            "status": "actuated",
            "joint_or_axis": joint_or_axis,
            "target_value": float(target_value),
            "speed_mps": speed_mps,
            "force_n": force_n,
        }

    def robot_navigate(
        self,
        x: float,
        y: float,
        z: float = 0.25,
        *,
        speed_mps: float = 0.25,
        frame_id: str = "base_link",
    ) -> dict[str, Any]:
        self._require_permission()
        self.envelope.validate_waypoint(x=x, y=y, z=z, speed_mps=speed_mps)
        self._position = {"x": float(x), "y": float(y), "z": float(z), "frame_id": frame_id}
        return {
            "schema": self.SCHEMA,
            "status": "navigated",
            "position": dict(self._position),
            "speed_mps": speed_mps,
        }

    def robot_stop_emergency(self, reason: str = "operator_e_stop") -> dict[str, Any]:
        self.envelope.emergency_stopped = True
        self.envelope.emergency_reason = reason
        return {
            "schema": self.SCHEMA,
            "status": "emergency_stopped",
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset_emergency_stop(self) -> dict[str, Any]:
        self._require_permission()
        self.envelope.emergency_stopped = False
        self.envelope.emergency_reason = None
        return {"schema": self.SCHEMA, "status": "e_stop_cleared"}
