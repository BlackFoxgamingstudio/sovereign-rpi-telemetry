#!/usr/bin/env python3
"""
Unit & Integration Test Suite for Raspberry Pi Edge Telemetry Daemon
Author: Russell Alan Powers
"""

import sys
import json
import unittest
import subprocess
from pathlib import Path

# Add solution root to path
SOLUTION_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOLUTION_ROOT))

from src.core import (
    poll_telemetry,
    evaluate_health,
    telemetry_to_dict,
    health_to_dict,
    TelemetrySnapshot,
    HardwareMetrics,
    SensorPayload
)


class TestRaspberryPiTelemetryDaemon(unittest.TestCase):

    def test_01_poll_telemetry_schema(self):
        """Verifies that poll_telemetry returns all required fields and valid types."""
        snapshot = poll_telemetry(simulate=True)
        self.assertIsInstance(snapshot, TelemetrySnapshot)
        self.assertTrue(snapshot.node_id.startswith("sbb-edge-"))
        self.assertIn("T", snapshot.timestamp)  # ISO 8601
        self.assertGreater(snapshot.hardware.cpu_temp_celsius, 0.0)
        self.assertGreaterEqual(snapshot.hardware.cpu_usage_percent, 0.0)
        self.assertLessEqual(snapshot.hardware.cpu_usage_percent, 100.0)
        self.assertTrue(snapshot.sensors.gpio_bus_active)

    def test_02_optimal_health_evaluation(self):
        """Verifies that standard hardware readings result in OPTIMAL status."""
        snapshot = poll_telemetry(simulate=True, thermal_spike=False)
        health = evaluate_health(snapshot)
        self.assertEqual(health.status, "OPTIMAL")
        self.assertEqual(health.alert_count, 0)
        self.assertEqual(len(health.alerts), 0)

    def test_03_thermal_spike_critical_alert(self):
        """Verifies that an injected thermal spike triggers a CRITICAL alert."""
        snapshot = poll_telemetry(simulate=True, thermal_spike=True)
        health = evaluate_health(snapshot)
        self.assertEqual(health.status, "CRITICAL")
        self.assertGreaterEqual(health.alert_count, 1)
        
        thermal_alerts = [a for a in health.alerts if a["code"] == "ERR_THERMAL_RUNAWAY"]
        self.assertEqual(len(thermal_alerts), 1)
        self.assertEqual(thermal_alerts[0]["severity"], "CRITICAL")
        self.assertGreaterEqual(thermal_alerts[0]["value"], 82.0)

    def test_04_memory_warning_threshold(self):
        """Verifies that elevated RAM usage triggers WARN_RAM_PRESSURE."""
        snapshot = poll_telemetry(simulate=True)
        # Artificially set RAM to 88%
        snapshot.hardware.ram_usage_percent = 88.0
        health = evaluate_health(snapshot)
        self.assertEqual(health.status, "WARNING")
        ram_alerts = [a for a in health.alerts if a["code"] == "WARN_RAM_PRESSURE"]
        self.assertEqual(len(ram_alerts), 1)

    def test_05_json_serialization(self):
        """Verifies serialization and deserialization via standard json."""
        snapshot = poll_telemetry(simulate=True)
        data = telemetry_to_dict(snapshot)
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["node_id"], snapshot.node_id)
        self.assertEqual(parsed["firmware_version"], "SBB-RPI-V2.4")

    def test_06_cli_poll_execution(self):
        """Runs the CLI entrypoint directly in simulation mode."""
        cli_path = SOLUTION_ROOT / "src" / "cli.py"
        res = subprocess.run(
            [sys.executable, str(cli_path), "--poll", "--simulate", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(res.returncode, 0)
        payload = json.loads(res.stdout)
        self.assertIn("hardware", payload)
        self.assertIn("cpu_temp_celsius", payload["hardware"])

    def test_07_cli_health_critical_exit_code(self):
        """Verifies CLI returns exit code 2 when critical threshold is breached."""
        cli_path = SOLUTION_ROOT / "src" / "cli.py"
        res = subprocess.run(
            [sys.executable, str(cli_path), "--health", "--simulate", "--thermal-spike"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(res.returncode, 2)  # Standard Unix Critical exit code
        payload = json.loads(res.stdout)
        self.assertEqual(payload["health"]["status"], "CRITICAL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
