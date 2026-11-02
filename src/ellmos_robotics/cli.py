"""CLI entrypoint for ellmos-robotics."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from .mcp_standard import RoboticsHub


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ellmos-robotics", description="ellmos.robotics.mcp.v1 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("capabilities", help="Show robot capabilities and safety envelope")
    sub.add_parser("telemetry", help="Show robot telemetry")

    act_p = sub.add_parser("actuate", help="Actuate a robot joint")
    act_p.add_argument("joint")
    act_p.add_argument("value", type=float)
    act_p.add_argument("--speed", type=float, default=0.2)
    act_p.add_argument("--force", type=float, default=5.0)

    nav_p = sub.add_parser("navigate", help="Navigate within 3D workspace bounds")
    nav_p.add_argument("x", type=float)
    nav_p.add_argument("y", type=float)
    nav_p.add_argument("z", type=float, default=0.25)

    stop_p = sub.add_parser("estop", help="Trigger immediate E-Stop")
    stop_p.add_argument("--reason", default="cli_e_stop")

    args = parser.parse_args(argv)
    hub = RoboticsHub()

    if args.cmd == "capabilities":
        print(json.dumps(hub.robot_capabilities(), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "telemetry":
        print(json.dumps(hub.robot_telemetry(), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "actuate":
        res = hub.robot_actuate(args.joint, args.value, speed_mps=args.speed, force_n=args.force)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "navigate":
        res = hub.robot_navigate(args.x, args.y, args.z)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "estop":
        res = hub.robot_stop_emergency(args.reason)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
