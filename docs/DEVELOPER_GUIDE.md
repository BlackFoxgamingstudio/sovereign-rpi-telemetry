# Developer Guide: Sovereign Raspberry Pi IoT Telemetry (`sovereign-rpi-telemetry`)

Welcome to the developer documentation for `sovereign-rpi-telemetry` (`PKG-001`). This guide provides comprehensive technical instructions for developers worldwide to set up, extend, configure, and integrate this IoT edge sensor daemon.

---

## 1. Quickstart & Local Setup

### Prerequisites
- Python 3.10+ (Standard library only; zero mandatory third-party dependencies)
- Git
- Optional: Docker & Docker Compose
- Optional: n8n 1.0+ for visual event orchestration

### Installation
```bash
# Clone the repository
git clone https://github.com/BlackFoxgamingstudio/sovereign-rpi-telemetry.git
cd sovereign-rpi-telemetry

# Copy environment configuration template
cp .env.example .env

# Install in editable development mode
pip install -e .

# Run test suite
pytest tests/test_solution.py -v
```

---

## 2. Variables & Configuration Matrix

Every aspect of the daemon can be configured via environment variables or n8n `$vars`:

| Variable Name | Default | Type | Description |
| :--- | :--- | :--- | :--- |
| `SBB_RPI_PORT` | `8770` | Integer | Microservice HTTP listener port |
| `SBB_RPI_HOST` | `0.0.0.0` | String | Network interface binding address |
| `SBB_NODE_ID` | Hostname | String | Unique hardware node identifier |
| `SBB_ENVIRONMENT` | `development` | String | Environment tier (`development`, `staging`, `production`) |
| `SBB_IOT_TEMP_WARNING_C` | `72.0` | Float | CPU temperature (°C) warning trip limit |
| `SBB_IOT_TEMP_CRITICAL_C` | `82.0` | Float | CPU temperature (°C) critical trip limit (triggers SRE failover) |
| `SBB_IOT_RAM_WARNING_PCT` | `80.0` | Float | System physical RAM (%) warning threshold |
| `SBB_IOT_RAM_CRITICAL_PCT` | `92.0` | Float | System physical RAM (%) critical threshold (OOM risk) |
| `SBB_IOT_DISK_CRITICAL_PCT`| `95.0` | Float | Storage volume utilization threshold |
| `SBB_VAULT_BRIDGE_URL` | `http://127.0.0.1:8766` | String | SBB Vault Bridge REST endpoint for audit events |
| `SBB_N8N_BASE_URL` | `http://127.0.0.1:5678` | String | n8n workflow engine base URL |

---

## 3. How to Extend: Adding Custom Sensor Metrics

The telemetry engine in `src/core.py` is designed for modular sensor expansion.

### Step-by-Step Tutorial: Adding an Ambient Humidity Sensor (DHT22 / I2C)
1. Open `src/core.py`.
2. Locate the `poll_hardware_metrics()` method.
3. Add your sensor extraction logic:
```python
def read_humidity(self) -> float:
    # Example reading from I2C bus or sysfs
    try:
        with open("/sys/bus/iio/devices/iio:device0/in_humidityrelative_input") as f:
            return round(float(f.read().strip()) / 1000.0, 1)
    except Exception:
        return 45.0  # Safe simulation baseline
```
4. Register the new metric in the returned hardware dictionary and add alert threshold rules in `evaluate_health()`.
5. Run the test suite:
```bash
pytest tests/test_solution.py -v
```

---

## 4. REST API Reference (Port 8770)

### `GET /healthz`
Returns basic daemon liveness.
```json
{
  "service": "Raspberry Pi Telemetry n8n Adapter",
  "status": "online",
  "version": "1.0.0"
}
```

### `GET /telemetry/health`
Returns full hardware sensor vitals, health status, and active alert list.
```json
{
  "summary": {
    "node_id": "sbb-edge-node-01",
    "cpu_temp": 46.5,
    "cpu_usage": 14.2,
    "ram_usage": 41.2
  },
  "health": {
    "status": "OPTIMAL",
    "alert_count": 0,
    "alerts": [],
    "evaluated_at": "2026-09-12T01:00:00Z"
  }
}
```

---

## 5. Deployment Options

### Option A: Direct Python Daemon
```bash
python3 n8n/webhook_adapter.py
```

### Option B: Linux systemd (Production Edge)
```bash
sudo cp templates/systemd/sbb-rpi-telemetry.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sbb-rpi-telemetry
```

### Option C: Docker Container
```bash
docker compose up -d
```
