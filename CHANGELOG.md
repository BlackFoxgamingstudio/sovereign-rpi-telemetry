# Changelog — Rpi Telemetry

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
Versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased] — v1.1.0 (Domain Business Logic Engine)
### In Progress
- Extracting and packaging granular component algorithms defined in docs/ARCHITECTURE.md.
- Connecting ChromaDB vector indexing and specialized domain pipelines.

## [1.0.0] — 2026-09-11 (Production DevOps & Automation Foundation)
### Added
- Multi-stage Dockerfile with non-root security context and health check.
- GitHub Actions CI matrix testing across Python 3.10, 3.11, and 3.12.
- Zero-Trust REST Webhook Adapter listening on port `8000` with `X-SBB-Auth` header validation.
- OpenAPI 3.1 interactive Swagger documentation (`/docs` and `/openapi.json`).
- Full n8n workflow canvas integration connecting Webhook ➔ HTTP Microservice ➔ Respond to Webhook.
- Architecture specification (`docs/ARCHITECTURE.md`), Developer Guide, SME Playbook, and SOP.
- Standardized CLI invocation harness in `src/cli.py`.
- Foundation CoreEngine with deterministic SHA-256 idempotency hashing.
