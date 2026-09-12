# Changelog

All notable changes to `sovereign-rpi-telemetry` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-12

### Added
- Zero-dependency Linux sysfs hardware telemetry collector (`cpu_temp`, `cpu_usage`, `ram_usage`, `disk_free`).
- Deterministic thermal runaway evaluation with dual trip thresholds (72.0°C warning, 82.0°C critical).
- Microservice webhook adapter on port 8770 with interactive Swagger UI (`/docs`) and OpenAPI 3.1 schema (`/openapi.json`).
- Automated incident escalation bridge into n8n and Solution 02 (`sovereign-avatar-agents`).
- Complete test suite with 100% pass rate under `pytest` and pure Python.
- GitHub Actions CI/CD matrix supporting Python 3.10–3.12 across Ubuntu and macOS.
- Multi-stage Dockerfile and Docker Compose templates for cloud and edge deployment.
