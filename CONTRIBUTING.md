# Contributing / Mitwirken

**English** | [Deutsch](#mitwirken-deutsch)

Thank you for your interest in contributing to `ellmos-robotics`!

## Ground Rules & Safety Invariants

1. **Zero Runtime Dependencies:** Keep the core package stdlib-only (`dependencies = []` in `pyproject.toml`).
2. **Fail-Closed Safety First:** Never weaken `RoboticsSafetyEnvelope`, permission checks (`robotics_permission`), or persisted E-Stop handling. An unreadable or malformed E-Stop file must always fail closed (`emergency_stopped = True`).
3. **E-Stop Always Allowed:** `robot_stop_emergency()` must remain callable even when `robotics_permission=False`.
4. **Honest Simulation Flag:** Any stubbed or simulated output must keep `"demo": true` until real, tested hardware drivers are explicitly designed and approved.
5. **Bilingual Parity:** Keep `README.md` (EN) and `README_de.md` (DE) synchronized.

## Development Workflow

```bash
git clone https://github.com/ellmos-ai/ellmos-robotics.git
cd ellmos-robotics
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pytest -ra -v
```

- Work on a dedicated feature or fix branch; open a Pull Request against `main`.
- Ensure `pytest -ra -v` passes with zero errors and `git diff --check` is clean before submitting.

---

<a id="mitwirken-deutsch"></a>
## Mitwirken (Deutsch)

Vielen Dank für dein Interesse an einem Beitrag zu `ellmos-robotics`!

### Grundregeln & Sicherheitsinvarianten

1. **Keine Laufzeitabhängigkeiten:** Das Kernpaket bleibt reine Python-Standardbibliothek (`dependencies = []` in `pyproject.toml`).
2. **Fail-Closed-Sicherheit zuerst:** `RoboticsSafetyEnvelope`, Berechtigungsprüfungen (`robotics_permission`) und die persistente E-Stop-Auswertung dürfen niemals abgeschwächt werden. Eine unlesbare oder defekte E-Stop-Datei muss immer fail-closed als gestoppt gelten.
3. **E-Stop immer erlaubt:** `robot_stop_emergency()` muss auch bei `robotics_permission=False` jederzeit aufrufbar bleiben.
4. **Ehrliche Demo-Kennzeichnung:** Simulierte oder gestubbte Ausgaben behalten `"demo": true`, bis echte, getestete Hardware-Treiber explizit freigegeben sind.
5. **Zweisprachige Parität:** `README.md` (EN) und `README_de.md` (DE) synchron pflegen.

### Entwicklungsablauf

```bash
git clone https://github.com/ellmos-ai/ellmos-robotics.git
cd ellmos-robotics
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pytest -ra -v
```

- Änderungen auf einem eigenen Branch umsetzen und als Pull Request gegen `main` einreichen.
- Vor dem Einreichen sicherstellen, dass `pytest -ra -v` vollständig grün ist und `git diff --check` keine Fehler meldet.
