# Contributing to Sovereign Raspberry Pi IoT Telemetry (`sovereign-rpi-telemetry`)

Thank you for your interest in contributing to the Sovereign Biz Box open-source ecosystem! We welcome contributions from developers worldwide.

---

## 1. Development Standards & Philosophy

1. **Zero Mandatory Runtime Dependencies**: The core library and microservice daemon must remain executable using only the Python standard library. Do not introduce mandatory third-party requirements for production execution.
2. **Deterministic Fallback Simulation**: Any sensor access logic must fall back gracefully to calibrated simulated baselines when run outside physical hardware (e.g., inside CI or Docker).
3. **100% Test Coverage**: All bug fixes and features must include unit and integration tests passing via both `pytest` and pure `python3 tests/test_solution.py`.

---

## 2. Setting Up Your Development Environment

```bash
# 1. Fork & clone the repository
git clone https://github.com/BlackFoxgamingstudio/sovereign-rpi-telemetry.git
cd sovereign-rpi-telemetry

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install in editable development mode
pip install -e ".[dev]" || pip install -e .

# 4. Run tests
pytest tests/test_solution.py -v
```

---

## 3. Pull Request Process

1. Create a feature branch from `main`: `git checkout -b feat/my-new-sensor`.
2. Follow Conventional Commits format (`feat:`, `fix:`, `docs:`, `refactor:`, `ci:`).
3. Ensure all tests pass locally across Python 3.10+.
4. Submit your PR using the provided pull request template.
5. All PRs must pass the automated GitHub Actions multi-OS test matrix before merge.
