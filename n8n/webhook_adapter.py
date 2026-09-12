#!/usr/bin/env python3
"""
SBB Edge Telemetry HTTP Adapter for n8n Automation
Author: Russell Alan Powers
Domain: IoT & Edge Systems
Exposes REST endpoints, OpenAPI 3.1, and Swagger UI on port 8770
"""

import sys
import os
import json
import signal
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib.parse

# Add solution root to path
SOLUTION_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOLUTION_ROOT))

from src.core import (
    poll_telemetry,
    evaluate_health,
    telemetry_to_dict,
    health_to_dict
)

PORT = int(os.environ.get("SBB_RPI_PORT", 8770))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [RpiAdapter] %(message)s")
logger = logging.getLogger("RpiAdapter")

OPENAPI_SPEC = {
    "openapi": "3.1.0",
    "info": {
        "title": "SBB Solution 01: Sovereign Raspberry Pi IoT Telemetry Daemon API",
        "description": "Zero-dependency IoT edge telemetry engine with hardware sensor polling, thermal trip evaluation, and automated incident cascading.",
        "version": "1.0.0",
        "contact": {"name": "Russell Alan Powers", "email": "russell@sovereignbizbox.io"}
    },
    "servers": [{"url": f"http://127.0.0.1:{PORT}", "description": "Local Edge Daemon"}],
    "paths": {
        "/healthz": {
            "get": {
                "summary": "Daemon Liveness & Health Check",
                "responses": {
                    "200": {
                        "description": "Daemon operational status",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/telemetry/health": {
            "get": {
                "summary": "Evaluate Live Hardware Sensors & Alerts",
                "description": "Polls physical host vitals (CPU temp, RAM, Disk) and evaluates threshold health.",
                "responses": {
                    "200": {
                        "description": "Health evaluation and summary",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/telemetry/poll": {
            "get": {
                "summary": "Poll Raw Telemetry Snapshot",
                "responses": {
                    "200": {
                        "description": "Detailed telemetry metrics",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/telemetry/simulate": {
            "post": {
                "summary": "Simulate Telemetry Event",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"thermal_spike": {"type": "boolean"}}
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Simulated evaluation result",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        }
    }
}

SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>SBB Solution 01 - Telemetry Daemon API</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    body { margin: 0; padding: 0; background: #fafafa; }
    .topbar { display: none; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis]
      });
    };
  </script>
</body>
</html>
"""

class TelemetryWebhookHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Correlation-ID")
        corr_id = self.headers.get("X-Correlation-ID")
        if corr_id:
            self.send_header("X-Correlation-ID", corr_id)
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path in ["", "/", "/healthz"]:
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "service": "Raspberry Pi Telemetry n8n Adapter",
                "status": "online",
                "version": "1.0.0",
                "docs_url": f"http://127.0.0.1:{PORT}/docs"
            }).encode("utf-8"))
            return

        if path == "/openapi.json":
            self._set_headers(200)
            self.wfile.write(json.dumps(OPENAPI_SPEC, indent=2).encode("utf-8"))
            return

        if path in ["/docs", "/swagger"]:
            self._set_headers(200, content_type="text/html; charset=utf-8")
            self.wfile.write(SWAGGER_UI_HTML.encode("utf-8"))
            return

        if path == "/telemetry/poll":
            snapshot = poll_telemetry(simulate=False)
            self._set_headers(200)
            self.wfile.write(json.dumps(telemetry_to_dict(snapshot), indent=2).encode("utf-8"))
            return

        if path == "/telemetry/health":
            snapshot = poll_telemetry(simulate=False)
            health = evaluate_health(snapshot)
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "health": health_to_dict(health),
                "summary": {
                    "node_id": snapshot.node_id,
                    "cpu_temp": snapshot.hardware.cpu_temp_celsius,
                    "cpu_usage": snapshot.hardware.cpu_usage_percent,
                    "ram_usage": snapshot.hardware.ram_usage_percent
                }
            }, indent=2).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": f"Endpoint not found: {path}"}).encode("utf-8"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/telemetry/simulate":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len) if content_len > 0 else b"{}"
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                payload = {}

            thermal_spike = bool(payload.get("thermal_spike", False))
            snapshot = poll_telemetry(simulate=True, thermal_spike=thermal_spike)
            health = evaluate_health(snapshot)

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "telemetry": telemetry_to_dict(snapshot),
                "health": health_to_dict(health)
            }, indent=2).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": f"Endpoint not found: {path}"}).encode("utf-8"))

    def log_message(self, fmt, *args):
        pass


def run_server():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), TelemetryWebhookHandler)
    logger.info(f"Raspberry Pi Telemetry Adapter listening on http://0.0.0.0:{PORT}")
    logger.info(f"Interactive Swagger UI: http://127.0.0.1:{PORT}/docs")

    def handle_signal(sig, frame):
        logger.info(f"Signal {sig} received. Initiating graceful shutdown...")
        server.server_close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        server.serve_forever()
    except Exception as e:
        logger.info(f"Server shutting down: {e}")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
