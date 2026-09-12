# Raspberry Pi Edge Telemetry Daemon & Hardware Monitor

**Package ID**: `sol-001-iot-telemetry-daemon`  
**Slug**: `raspberry-pi-telemetry-daemon`  
**Author**: Russell Alan Powers  
**Target Role**: Staff IoT & Edge Systems Architect | Principal Embedded SRE  
**Language**: Python 3.9+ (Zero External Dependencies)  
**Status**: Production-Ready  

---

## 1. Executive Architecture

The Raspberry Pi Edge Telemetry Daemon is a lightweight, non-blocking hardware monitoring and telemetry engine built for edge computing environments, IoT gateways, and industrial field controllers.

```mermaid
flowchart LR
    subgraph EdgeDevice["Raspberry Pi / IoT Node"]
        SENSORS[I2C/GPIO Sensors] --> CORE[Telemetry Core Engine]
        SYSFS[/sys/class/thermal] --> CORE
        PROC[/proc/meminfo] --> CORE
        CORE --> CLI[cli.py Interface]
        CORE --> HTTP_ADAPTER[n8n Webhook Adapter :8770]
    end

    subgraph Automation["Automation & Telemetry Plane"]
        CLI --> N8N[n8n Workflow Engine]
        HTTP_ADAPTER --> N8N
        N8N --> TELEMETRY_DB[(facility_telemetry_v2.db)]
        N8N --> ALERTS[Incident Alert Dispatcher]
    end
```

### Key Technical Capabilities:
- **Zero-Dependency Core**: Operates strictly on Python standard library modules (`os`, `sys`, `subprocess`, `dataclasses`, `datetime`, `shutil`), ensuring instant deployment on resource-constrained embedded targets.
- **Dynamic Hardware Abstraction**: Auto-detects Linux sysfs thermal zones, `vcgencmd`, macOS POSIX load averages, and includes a high-fidelity simulation engine for CI/CD and regression testing.
- **Autonomous SLA Threshold Evaluation**: Real-time classification of operational health into `OPTIMAL`, `WARNING`, and `CRITICAL` states with standardized Unix exit codes (0, 1, 2).
- **n8n Automation Integration**: Native CLI execution node and local HTTP webhook adapter (`:8770`) for event-driven telemetry ingestion and incident dispatch.

---

## 2. CLI Quick Reference

```bash
# 1. Run immediate telemetry poll (JSON output)
python3 src/cli.py --poll

# 2. Evaluate hardware health against safety thresholds
python3 src/cli.py --health

# 3. Simulate hardware readings (for CI/CD testing)
python3 src/cli.py --poll --simulate

# 4. Inject a thermal runaway spike (>82°C) to verify alert pipelines
python3 src/cli.py --health --simulate --thermal-spike
# Returns exit code 2 (CRITICAL) and ERR_THERMAL_RUNAWAY payload
```

---

## 3. Sample Telemetry Schema (RFC 3339)

```json
{
  "timestamp": "2026-09-11T22:52:00.000000+00:00",
  "node_id": "sbb-edge-blackloin45-GODISBLACK",
  "architecture": "arm64",
  "os_release": "Darwin 24.6.0",
  "hardware": {
    "cpu_temp_celsius": 46.5,
    "cpu_usage_percent": 18.5,
    "ram_usage_percent": 41.2,
    "ram_available_mb": 4820.0,
    "disk_usage_percent": 54.0,
    "disk_free_gb": 120.5,
    "uptime_seconds": 86400.0,
    "load_average": [0.5, 0.5, 0.5]
  },
  "sensors": {
    "device_id": "bme280-edge-bus-1",
    "gpio_bus_active": true,
    "i2c_bus_active": true,
    "spi_bus_active": false,
    "ambient_temp_c": 22.4,
    "relative_humidity_pct": 46.2,
    "vibration_g": 0.03,
    "signal_strength_dbm": -58
  },
  "firmware_version": "SBB-RPI-V2.4"
}
```

---

## 4. Verification Suite

Run the built-in automated test suite:

```bash
python3 tests/test_solution.py
```
*Tests verify field types, metric boundaries, thermal thresholds, memory warnings, JSON serialization, and CLI exit codes.*
