"""Contract tests for bilingual README parity, P-022 LLM readiness, SVG assets, and metadata."""

from __future__ import annotations

import json
import re
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

from ellmos_robotics import __version__

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_version_freeze_and_pep639_metadata():
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    assert project["version"] == "0.1.0"
    assert __version__ == "0.1.0"
    assert project["license"] == "MIT"
    assert not any(c.startswith("License ::") for c in project.get("classifiers", []))
    assert len(project.get("keywords", [])) >= 10
    assert "Homepage" in project.get("urls", {})
    assert "LLM Entry" in project.get("urls", {})

    manifest = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))
    assert manifest["version"] == project["version"]


def test_readme_bilingual_parity_and_anchors():
    en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "[Deutsch](README_de.md)" in en
    assert "[English](README.md)" in de
    assert "assets/banner.svg" in en and "assets/banner.svg" in de
    assert "assets/terminal-workflow.svg" in en and "assets/terminal-workflow.svg" in de

    expected_anchors = [f"sec-0{i}-" for i in range(1, 10)]
    for prefix in expected_anchors:
        assert f'id="{prefix}' in en, f"Missing anchor {prefix} in README.md"
        assert f'id="{prefix}' in de, f"Missing anchor {prefix} in README_de.md"

    assert "```mermaid" in en and "sequenceDiagram" in en and "flowchart TD" in en
    assert "```mermaid" in de and "sequenceDiagram" in de and "flowchart TD" in de


def test_p022_llm_readiness_files():
    skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
    llms = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")
    llm = (REPO_ROOT / "llm.txt").read_text(encoding="utf-8")

    assert "version: 0.1.0" in skill
    assert "ellmos.robotics.mcp.v1" in skill
    assert '"demo": true' in skill

    assert "Version: `0.1.0`" in llms
    assert "Last-checked: `2026-11-22`" in llms
    assert "SKILL.md" in llms
    assert "llms.txt" in llm


def test_svg_assets_are_well_formed():
    for rel in ("assets/banner.svg", "assets/terminal-workflow.svg"):
        svg_path = REPO_ROOT / rel
        assert svg_path.is_file()
        root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
        assert root.tag.endswith("svg")
        assert "viewBox" in root.attrib


def test_community_governance_and_changelog_unreleased():
    for rel in ("CHANGELOG.md", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md", "SECURITY.md", "LICENSE"):
        assert (REPO_ROOT / rel).is_file()

    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog
    assert "## [0.1.0]" in changelog


def test_public_attribution_uses_geiger_not_lg():
    for rel in ("README.md", "README_de.md"):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "Geiger" in text
        assert not re.search(r"\bLG\b", text)
