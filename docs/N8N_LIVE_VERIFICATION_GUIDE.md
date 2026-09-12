# Live n8n Solution 01 Verification & Credentials Guide

## Service Overview
- **Solution Name**: SBB Solution 01 - Raspberry Pi IoT Telemetry & Alert Dispatcher
- **PyPI Package**: `sovereign-rpi-telemetry`
- **Location**: `/Users/russellpowers/Sovereign Biz Box/solutions/raspberry-pi-telemetry-daemon`
- **Domain**: IoT & Edge Systems
- **Status**: **PRODUCTION_READY (LIVE & TESTED)**

---

## 1. Login Information & Access

| Service | Address | Credentials / Auth |
| :--- | :--- | :--- |
| **n8n Web Console** | [http://localhost:5678](http://localhost:5678) | **Email**: `russell@sovereignbizbox.io`<br>**Password**: `SovereignBizBox2026!` |
| **Active Workflow** | In n8n under "Workflows" | Name: **"SBB Solution 01: Raspberry Pi IoT Telemetry & Alert Dispatcher"** |
| **Webhook Inbound Route** | `POST http://127.0.0.1:5678/webhook/rpi-telemetry` | Public LAN Webhook (No auth required for edge nodes) |
| **Telemetry Webhook Adapter** | [http://127.0.0.1:8770](http://127.0.0.1:8770) | Endpoints: `/healthz`, `/telemetry/poll`, `/telemetry/health` |
| **SBB Vault REST Bridge** | [http://127.0.0.1:8766](http://127.0.0.1:8766) | Endpoints: `/health`, `/api/solutions`, `/api/webhook/audit` |

---

## 2. Live Services Architecture

```
┌────────────────────────────────────────────────────────┐
│                   IoT Edge Ingestion                   │
│   (cURL, Python Daemon, or Scheduled Cron Trigger)     │
└────────────────────────────────────────────────────────┘
                           │
                           │  HTTP POST /webhook/rpi-telemetry
                           ▼
┌────────────────────────────────────────────────────────┐
│             n8n Enterprise Workflow Engine             │
│                    (Port 5678)                         │
│                                                        │
│  1. Ingests Telemetry Payload                          │
│  2. Evaluates Hardware Metrics (CPU Temp, RAM, Disk)   │
│  3. Detects Critical Anomalies (>82°C Thermal Spike)   │
│  4. Determines State: OPTIMAL vs. CRITICAL             │
└────────────────────────────────────────────────────────┘
                           │
                           │  HTTP POST /api/webhook/audit
                           ▼
┌────────────────────────────────────────────────────────┐
│             SBB Codebase Vault REST Bridge             │
│                    (Port 8766)                         │
└────────────────────────────────────────────────────────┘
                           │
                           │  Writes Incident / Heartbeat Log
                           ▼
┌────────────────────────────────────────────────────────┐
│      Telemetry Database: facility_telemetry_v2.db      │
│          Table: n8n_automation_telemetry               │
└────────────────────────────────────────────────────────┘
```

---

## 3. Step-by-Step Verification Instructions

### Step 1: Open n8n in Your Browser
1. Open your browser and navigate to: **[http://localhost:5678](http://localhost:5678)**
2. Enter your credentials:
   - **Email**: `russell@sovereignbizbox.io`
   - **Password**: `SovereignBizBox2026!`
3. You will be greeted by the **Sovereign Biz Box Command Center** project.
4. Click on **Workflows** to see **"SBB Solution 01: Raspberry Pi IoT Telemetry & Alert Dispatcher"** marked with a green **Active** badge.
5. Click **Executions** in the left sidebar to see the real-time execution log.

---

### Step 2: Trigger Normal Telemetry Heartbeat
Run this command from your terminal to simulate a standard hardware heartbeat:

```bash
curl -X POST http://127.0.0.1:5678/webhook/rpi-telemetry \
  -H "Content-Type: application/json" \
  -d '{"simulate": true}'
```

**Expected Response**:
```json
{"success": true, "telemetry_id": 3}
```
*Result: Status `OPTIMAL`, 0 alerts, logged as `iot_telemetry_heartbeat` in SQLite.*

---

### Step 3: Trigger Thermal Runaway Critical Incident
Run this command to simulate an overheating industrial Raspberry Pi CPU (86.4°C):

```bash
curl -X POST http://127.0.0.1:5678/webhook/rpi-telemetry \
  -H "Content-Type: application/json" \
  -d '{"thermal_spike": true}'
```

**Expected Response**:
```json
{"success": true, "telemetry_id": 4}
```
*Result: Status `CRITICAL`, alerts generated for `ERR_THERMAL_RUNAWAY` (86.4°C) and `ERR_OOM_RISK` (94.2% RAM), dispatched as `iot_hardware_incident`.*

---

### Step 4: Verify the Recorded Events in the Database
Run this query to inspect the records stored in SQLite:

```bash
python3 -c "
import sqlite3, json

conn = sqlite3.connect('/Users/russellpowers/Sovereign Biz Box/databases/facility_telemetry_v2.db')
c = conn.cursor()
c.execute('SELECT id, timestamp, event_name, source, details FROM n8n_automation_telemetry ORDER BY id DESC LIMIT 2')
for row in c.fetchall():
    print(f'=== Log ID: {row[0]} | Event: {row[2]} | Time: {row[1]} ===')
    print(json.dumps(json.loads(row[4]), indent=2))
"
```

---

### Step 5: Test the Standalone Microservice Directly
Verify the zero-dependency Python adapter running independently on port 8770:

```bash
# Health check
curl -s http://127.0.0.1:8770/healthz

# Live host telemetry evaluation
curl -s http://127.0.0.1:8770/telemetry/health
```

---

## 4. Service Management & Troubleshooting

To stop all services:
```bash
bash "/Users/russellpowers/Sovereign Biz Box/sbb-n8n-command-center/stop_local_n8n.sh"
```

To restart the full stack:
```bash
python3 "/Users/russellpowers/Sovereign Biz Box/sbb-n8n-command-center/run_solution_01_stack.py"
```
