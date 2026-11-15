# ellmos-robotics

[English](README.md) | **Deutsch**

Werkzeugstandard `ellmos.robotics.mcp.v1` für die Kommunikation von LLMs mit Robotern im ellmos-Ökosystem (BACH, Open Ocean): ein Hub mit fünf Roboter-Werkzeugen, eine Sicherheitshülle (Geschwindigkeit, Kraft, Arbeitsraumgrenzen, E-Stop) und Treiberprofile. Ein kleines, abhängigkeitsfreies Python-Paket.

> **Status: early (v0.1.0), nur Simulation.** Die Treiberklassen (`ros2_bridge`, `serial_esp32`, `lerobot_embodied`, `mavlink_rover`) sind Stubs mit Kennung und Protokollname; keine davon spricht mit Hardware. Alle Hub-Ergebnisse stammen aus simuliertem Speicherzustand und tragen `"demo": true`. Die Sicherheitslogik (Hüllenprüfung, persistenter E-Stop) ist echt und getestet, das Paket darf in diesem Zustand aber nicht zur Bewegung physischer Hardware verwendet werden.

## Funktionen

- **`RoboticsHub`** implementiert die Werkzeugoberfläche:
  - `robot_capabilities()`: Treiber, Gelenke (`shoulder_pan`, `elbow_flex`, `wrist_roll`, `gripper`), Koordinatenrahmen, aktuelle Sicherheitshülle
  - `robot_telemetry()`: simulierte Position, Gelenkwerte, Batterie, E-Stop- und Kollisionszonen-Flags, Zeitstempel
  - `robot_actuate(joint, value, speed_mps=0.2, force_n=5.0)`
  - `robot_navigate(x, y, z=0.25, speed_mps=0.25, frame_id="base_link")`
  - `robot_stop_emergency(reason)`: immer erlaubt, auch ohne Robotik-Berechtigung
  - `reset_emergency_stop()`: erfordert Robotik-Berechtigung
- **`RoboticsSafetyEnvelope`** (Standardwerte): max. Geschwindigkeit 0,5 m/s, max. Kraft 15 N, Arbeitsraum x und y in [-2, 2], z in [0, 1,8]. Eine Anfrage wird mit `RoboticsSafetyViolationError` abgelehnt, wenn der E-Stop aktiv ist, `human_in_collision_zone` gesetzt ist, Geschwindigkeit oder Kraft zu hoch sind oder ein Wegpunkt außerhalb der Grenzen liegt.
- **Persistenter E-Stop (fail-closed):** Der Stopp wird atomar in eine Zustandsdatei geschrieben und von jeder neuen Hub-Instanz übernommen. Eine unlesbare oder fehlerhafte Zustandsdatei gilt als gestoppt. Standardpfad ist `~/.bach/robotics_estop.json`, überschreibbar über die Umgebungsvariable `BACH_ROBOTICS_ESTOP_PATH`, das Argument `state_path` oder die CLI-Option `--state-path`.
- **Berechtigungs-Gate:** Mit `robotics_permission=False` lösen alle Werkzeuge außer dem E-Stop `PermissionError` aus.

## Installation

Benötigt Python 3.10 oder neuer; es gibt keine Laufzeitabhängigkeiten. Aus einem Klon:

```bash
pip install -e .
pip install -e ".[dev]"   # pytest
```

## Nutzung

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
# jedes weitere robot_actuate / robot_navigate löst nun RoboticsSafetyViolationError aus
```

Hinweis: Der CLI-Befehl `estop` schreibt die gemeinsame E-Stop-Datei; zurückgesetzt wird sie in Python mit `reset_emergency_stop()` oder durch Löschen der Zustandsdatei. Die Tests liegen in `tests/test_robotics.py` (Aufruf mit `pytest`).

## Bezug zu ellmos und Open Ocean

`ellmos-robotics` gehört zu den Erweiterungsmodulen in der Modulzuordnung von [Open Ocean](https://github.com/ellmos-ai/open-ocean). Die Hülle hat ein Flag `human_in_collision_zone`, das von [ellmos-sensation](https://github.com/ellmos-ai/ellmos-sensation) gespeist werden soll; diese Kopplung ist in diesem Repository nicht umgesetzt. Die Modul-Metadaten stehen in `ellmos-module.v2.json`.

## Lizenz

MIT, wie in `pyproject.toml` angegeben.
