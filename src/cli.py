#!/usr/bin/env python3
"""
Raspberry Pi Edge Telemetry CLI Interface
Author: Russell Alan Powers
Domain: IoT & Edge Systems
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path to allow relative import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core import (
    poll_telemetry,
    evaluate_health,
    telemetry_to_dict,
    health_to_dict
)


def main():
    parser = argparse.ArgumentParser(
        description="Raspberry Pi Edge Telemetry Daemon CLI"
    )
    parser.add_argument("--poll", action="store_true", help="Poll hardware and output full telemetry snapshot")
    parser.add_argument("--health", action="store_true", help="Evaluate telemetry against safety thresholds")
    parser.add_argument("--simulate", action="store_true", help="Simulate telemetry data (for tests/CI)")
    parser.add_argument("--thermal-spike", action="store_true", help="Inject thermal spike into simulation")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format (default: json)")

    args = parser.parse_args()

    # Default to poll if no specific mode is requested
    if not (args.poll or args.health):
        args.poll = True

    snapshot = poll_telemetry(simulate=args.simulate, thermal_spike=args.thermal_spike)
    health = evaluate_health(snapshot)

    if args.health:
        if args.format == "json":
            out = {
                "health": health_to_dict(health),
                "telemetry_summary": {
                    "node_id": snapshot.node_id,
                    "cpu_temp": snapshot.hardware.cpu_temp_celsius,
                    "cpu_usage": snapshot.hardware.cpu_usage_percent,
                    "ram_usage": snapshot.hardware.ram_usage_percent
                }
            }
            print(json.dumps(out, indent=2))
        else:
            print(f"Node: {snapshot.node_id} | Status: {health.status} | Alerts: {health.alert_count}")
            for a in health.alerts:
                print(f"  [{a['severity']}] {a['code']}: {a['message']}")
        
        # Exit code reflects health status
        if health.status == "CRITICAL":
            sys.exit(2)
        elif health.status == "WARNING":
            sys.exit(1)
        sys.exit(0)

    if args.poll:
        telemetry_dict = telemetry_to_dict(snapshot)
        if args.format == "json":
            print(json.dumps(telemetry_dict, indent=2))
        else:
            hw = snapshot.hardware
            print(f"=== SBB EDGE TELEMETRY: {snapshot.node_id} ===")
            print(f"Timestamp:   {snapshot.timestamp}")
            print(f"CPU Temp:    {hw.cpu_temp_celsius} °C")
            print(f"CPU Usage:   {hw.cpu_usage_percent} %")
            print(f"RAM Usage:   {hw.ram_usage_percent} %")
            print(f"Disk Usage:  {hw.disk_usage_percent} % (Free: {hw.disk_free_gb} GB)")
            print(f"Sensors:     Ambient {snapshot.sensors.ambient_temp_c} °C, RH {snapshot.sensors.relative_humidity_pct} %")
            print(f"Health:      {health.status}")
        sys.exit(0)


if __name__ == "__main__":
    main()
