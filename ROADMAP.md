# Engineering Roadmap & Implementation Status — Rpi Telemetry

**Package ID**: `PKG-000`  
**Domain**: Enterprise Software Engineering  
**Microservice Port**: `http://127.0.0.1:8000`  
**Architecture Classification**: TIER 2 (INFRASTRUCTURE LIVE / LOGIC QUEUED)  

---

## 1. Architectural Maturity Level

**Tier 2: Foundation & Integration Live**. Docker containerization, GitHub Actions CI/CD, OpenAPI 3.1 REST API, Zero-Trust `X-SBB-Auth` webhook adapter, and n8n canvas nodes are fully production-ready. Domain algorithms are documented in `docs/ARCHITECTURE.md` and tracked on the `ROADMAP.md` backlog.

### Platform Maturity Matrix
| Layer | Capability | Status | Notes |
|---|---|---|---|
| **DevOps & Packaging** | Multi-stage Dockerfile, pyproject.toml | ✅ Complete | Non-root OCI compliant container |
| **CI/CD** | GitHub Actions Workflow | ✅ Complete | Python 3.10 / 3.11 / 3.12 test matrix |
| **Networking & API** | REST Microservice (`PORT 8000`) | ✅ Complete | OpenAPI 3.1 spec, Swagger UI at `/docs` |
| **Security** | Zero-Trust Authorization | ✅ Complete | `X-SBB-Auth` header authentication enforced |
| **Automation** | n8n Canvas Integration | ✅ Complete | 3-node connected pipeline active on port 5678 |
| **Domain Logic** | Core Component Algorithms | ⏳ Queued (Tier 2) | See Feature Backlog below |

---

## 2. Feature Backlog & Component Status

### Component 1: `SysfsThermalPoller`
- **Role**: Direct Linux kernel sysfs thermal zone poller
- **Current Status**: ⏳ Queued for v1.1.0 Implementation
- **Integration**: Exposed via `POST /api/v1/execute` with action `sysfsthermalpoller`
- **Verification Strategy**: Dedicated `unittest.TestCase` validating deterministic output and idempotency.

### Component 2: `ProcLoadReader`
- **Role**: POSIX /proc/loadavg and memory saturation analyzer
- **Current Status**: ⏳ Queued for v1.1.0 Implementation
- **Integration**: Exposed via `POST /api/v1/execute` with action `procloadreader`
- **Verification Strategy**: Dedicated `unittest.TestCase` validating deterministic output and idempotency.

### Component 3: `I2CSensorQuery`
- **Role**: Hardware bus I2C/GPIO ambient sensor reader
- **Current Status**: ⏳ Queued for v1.1.0 Implementation
- **Integration**: Exposed via `POST /api/v1/execute` with action `i2csensorquery`
- **Verification Strategy**: Dedicated `unittest.TestCase` validating deterministic output and idempotency.

### Component 4: `GestureClassifier`
- **Role**: Kinematic trajectory swipe and pinch gesture classifier
- **Current Status**: ⏳ Queued for v1.1.0 Implementation
- **Integration**: Exposed via `POST /api/v1/execute` with action `gestureclassifier`
- **Verification Strategy**: Dedicated `unittest.TestCase` validating deterministic output and idempotency.

### Component 5: `CrashDumpBundler`
- **Role**: Automated tar.gz diagnostic crash dump packager with SHA-256
- **Current Status**: ⏳ Queued for v1.1.0 Implementation
- **Integration**: Exposed via `POST /api/v1/execute` with action `crashdumpbundler`
- **Verification Strategy**: Dedicated `unittest.TestCase` validating deterministic output and idempotency.


---

## 3. Implementation Workflow for Domain Engineers

1. Create discrete module file: `src/rpi_telemetry_<component>.py`
2. Implement core algorithmic methods adhering to zero external third-party dependencies where feasible.
3. Import into `src/core.py` and register in `CoreEngine.execute_feature()`.
4. Author comprehensive test cases in `tests/test_solution.py`.
5. Run automated test harness: `python3 -m unittest discover -s tests`
6. Sync completion status in `databases/sbb_packaged_solutions.db`.
