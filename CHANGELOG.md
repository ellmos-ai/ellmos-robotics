# Changelog

All notable changes to `ellmos-robotics` are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Dark-mode terminal & safety-envelope preview SVG (`assets/terminal-workflow.svg`).
- Bilingual 9-section README architecture (`README.md` & `README_de.md`) with Shields.io badges, anchor navigation, Mermaid architecture flowchart (`flowchart TD`), and fail-closed E-Stop lifecycle `sequenceDiagram`.
- Policy P-022 LLM-readiness files (`SKILL.md`, `llms.txt`, `llm.txt`) and copyable LLM installation prompts.
- Community and governance documentation (`CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/`).
- PEP 621 `keywords` and `[project.urls]` metadata in `pyproject.toml` (version `0.1.0` unchanged).
- Metadata and bilingual README parity contract tests (`tests/test_metadata.py`).

## [0.1.0] - 2026-11-02

### Added
- Initial `ellmos.robotics.mcp.v1` tool surface (`RoboticsHub`), `RoboticsSafetyEnvelope`, persistent fail-closed E-Stop (`~/.bach/robotics_estop.json` / `BACH_ROBOTICS_ESTOP_PATH`), permission gating, CLI (`ellmos-robotics`), and simulation driver stubs (`ros2_bridge`, `serial_esp32`, `lerobot_embodied`, `mavlink_rover`).
- Repository header banner (`assets/banner.svg`, `assets/banner.png`), MIT `LICENSE`, and bilingual `README_de.md`.
