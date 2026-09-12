# ADR 0001: Initial Architecture and Technology Stack

## Status
Accepted

## Context
The Sovereign Biz Box (SBB) platform requires a standardized, scalable, and secure architecture across all its micro-solutions. This specific solution (`raspberry-pi-telemetry-daemon`) needs to integrate seamlessly with the n8n-driven Central Event Bus, operate securely on edge devices or central mainframes, and maintain high developer ergonomics. We needed to select the language, transport mechanism, packaging strategy, and CI/CD approach.

## Decision
We have adopted the following architectural standards for this solution:

1. **Language & Runtime**: Python 3.10+ using `pyproject.toml` (src-layout).
   * *Why*: Python provides the most mature ecosystem for AI, ML, and data integrations (which are core to SBB). The src-layout prevents import errors during testing and ensures clean packaging.
2. **Integration / Transport**: HTTP REST Webhooks (Default Port: `8770`) connected to n8n.
   * *Why*: Rather than complex message brokers (Kafka/RabbitMQ) which add heavy operational overhead for edge deployments, simple HTTP webhooks provide robust, debuggable, and native integration with n8n's event-driven architecture.
3. **Containerization**: Multistage Docker with non-root execution (UID 1001).
   * *Why*: Security-first design. Multistage builds keep images small, and running as a non-root user prevents privilege escalation on host systems.
4. **API Design**: OpenAPI 3.1 Envelope Pattern.
   * *Why*: Every request uses an `{action, payload, trace_id}` envelope to standardize parsing and error handling across 30+ disparate domains.
5. **Testing & CI/CD**: Pytest, Ruff, and GitHub Actions.
   * *Why*: Standardizing on Ruff replaces multiple linters (Flake8, isort). GitHub Actions matrix builds ensure cross-version compatibility before deployment.

## Consequences
* **Positive**: Rapid bootstrapping for developers, unified CI/CD pipelines, consistent security posture, and seamless n8n orchestration.
* **Negative**: HTTP webhooks may require retry logic (DLQ) for transient network failures compared to persistent message queues.
* **Mitigation**: A Global Dead Letter Queue (DLQ) workflow in n8n is used to catch and retry failed webhook deliveries.
