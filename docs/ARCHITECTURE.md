# Architecture & Engineering Specification: `sovereign-rpi-telemetry`

## 1. Architectural Philosophy

`sovereign-rpi-telemetry` is engineered around three core design principles:
1. **Zero Mandatory Runtime Dependencies**: Built entirely using the Python standard library (`http.server`, `urllib`, `dataclasses`, `sysfs`). It runs flawlessly on resource-constrained embedded systems without heavy dependency footprints.
2. **Deterministic Fallback Simulation**: When hardware sensors (sysfs thermal zones, I2C devices) are unavailable—such as inside non-privileged Docker containers or CI environments—the engine falls back to calibrated simulation curves rather than crashing.
3. **Closed-Loop Anomaly Propagation**: Rather than passively recording metrics, the daemon proactively detects threshold breaches and triggers automated remediation through n8n workflows and downstream SRE avatar agents.

---

## 2. Sequence Diagram: Edge Telemetry to SRE Healing

```
Hardware Sensor        Telemetry Daemon         n8n Router          Avatar SRE        Vault Bridge
   (/sysfs)                (:8770)               (:5678)              (:8785)           (:8766)
      │                       │                     │                    │                 │
      │── Read CPU Temp ─────>│                     │                    │                 │
      │   (86.4°C Spike)      │                     │                    │                 │
      │                       │── Status: CRITICAL ─>│                    │                 │
      │                       │   Alerts: [RUNAWAY] │                    │                 │
      │                       │                     │── Audit Incident ───────────────────>│
      │                       │                     │                     │        (Persist)
      │                       │                     │── Route Anomaly ──>│                 │
      │                       │                     │   (POST webhook)   │                 │
      │                       │                     │                    │── Diagnoses     │
      │                       │                     │                    │── Remediation ─>│
      │                       │                     │                    │   Directives    │
```

---

## 3. Threat Modeling & Fault Tolerance

- **Network Partitioning**: If the upstream n8n engine or Vault Bridge is unreachable, the daemon logs locally and continues polling sensors without memory accumulation.
- **Sensor Failure**: Broken sysfs paths return structured `METRIC_UNAVAILABLE` warnings instead of unhandled exceptions.
- **Denial of Service**: The embedded HTTP daemon enforces request timeouts and small maximum buffer limits.
