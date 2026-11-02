# ellmos-robotics

Kanonischer MCP-Standard (`ellmos.robotics.mcp.v1`), Treiber-Adapter und Sicherheits-Envelope für die Kommunikation von LLMs mit Robotern und physischen Aktuatoren (`OCEAN-ROBOTICS-01`, BACH `#3767` / Ocean `#537`).

## MCP-Standard `ellmos.robotics.mcp.v1`

- `robot_capabilities`: Freiheitsgrade (DOF), Sensoren, Koordinatenrahmen, Sicherheitsgrenzen (Maximalgeschwindigkeit, Kraftlimit, 3D-Bounding-Box).
- `robot_telemetry`: Echtzeit-Position, Gelenkwinkel, Batteriestatus, Hindernisdistanz, E-Stop-Status.
- `robot_actuate`: Sichere Gelenk-/Greifer-/Servo-Steuerung mit Kraft- und Geschwindigkeits-Gate.
- `robot_navigate`: 2D/3D-Wegpunktnavigation mit Bounding-Box- und Kollisionsprüfung.
- `robot_stop_emergency`: Sofortiger Hardware-/Software-Not-Aus (E-Stop Latch).

## Treiber-Profile

- `Ros2BridgeDriver` (`ros2_bridge`)
- `SerialEsp32Driver` (`serial_esp32`)
- `LeRobotDriver` (`lerobot_embodied`)
- `MavlinkDroneDriver` (`mavlink_rover`)
