# Standard Operating Procedure (SOP): Raspberry Pi Edge Telemetry Daemon

**Document Ref**: `SOP-IOT-001`  
**Revision**: `2.0`  
**Applicability**: Edge Gateways, Raspberry Pi Compute Modules, IoT Field Sensors  
**Owner**: Russell Alan Powers  

---

## 1. Purpose & Scope
This Standard Operating Procedure defines the deployment, routine monitoring, automated execution, and incident triage protocol for the **Raspberry Pi Edge Telemetry Daemon** (`raspberry-pi-telemetry-daemon`).

---

## 2. Deployment Protocols

### Option A: Automated Execution via n8n (Recommended)
1. Open local n8n at `http://localhost:5678` or private Mac Mini n8n at `http://192.168.50.2:5678`.
2. Navigate to **Workflows** $\rightarrow$ **+ Add Workflow** $\rightarrow$ **⋮** $\rightarrow$ **Import from File**.
3. Select `/Users/russellpowers/Sovereign Biz Box/solutions/raspberry-pi-telemetry-daemon/n8n/workflow.json`.
4. Toggle the workflow to **Active**.
5. The workflow will automatically execute every 5 minutes and listen on `POST /webhook/rpi-telemetry` for on-demand polling.

### Option B: Linux Systemd Daemon Deployment (Edge Hardware)
To run as a 24/7 background service on a physical Raspberry Pi:
```ini
# /etc/systemd/system/sbb-telemetry.service
[Unit]
Description=SBB Edge Telemetry Daemon
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/sbb/solutions/raspberry-pi-telemetry-daemon
ExecStart=/usr/bin/python3 src/cli.py --poll
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Reload and enable systemd:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sbb-telemetry.service
```

---

## 3. Incident Triage Runbook

| Incident Code | Severity | Description | Immediate Action |
| :--- | :---: | :--- | :--- |
| `ERR_THERMAL_RUNAWAY` | **CRITICAL** | CPU temp $\ge 82^\circ\text{C}$ | 1. Check fan header / active cooling.<br>2. Inspect CPU throttle state via `vcgencmd get_throttled`.<br>3. Terminate runaway processes with `top -o %CPU`. |
| `WARN_THERMAL_ELEVATED` | **WARNING** | CPU temp $\ge 72^\circ\text{C}$ | 1. Verify ambient enclosure airflow.<br>2. Reduce background batch processing. |
| `ERR_OOM_RISK` | **CRITICAL** | RAM utilization $\ge 92\%$ | 1. Identify memory leaks using `ps aux --sort=-%mem`.<br>2. Restart heavy microservices.<br>3. Check swap space via `free -m`. |
| `ERR_DISK_FULL` | **CRITICAL** | Root partition $\ge 90\%$ | 1. Purge rotated logs in `/var/log`.<br>2. Clean docker container cache via `docker system prune -f`. |

---

## 4. Verification Check
Execute the health check command:
```bash
python3 src/cli.py --health
echo "Exit status: $?"
```
*Expected exit code:* `0` (*OPTIMAL*).
