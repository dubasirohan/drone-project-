"""
analysis_server.py — AI Analysis & Dashboard Server with ESP32 Hardware Integration.

Responsibilities:
1. Grabs frames from gopro_client.py (HTTP GET /capture)
2. Runs YOLOv8n person detection
3. Grid-based zone counting (3 rows x 4 cols)
4. Density classification per zone
5. Alert generation for high-density zones
6. Wireless ESP32 audio & crowd management bridge (TCP port 8002)
   - Built-in DAC audio out on GPIO 25 (sirens, voice announcements)
   - Physical trigger button input on GPIO 14
7. WebSocket broadcast of telemetry, crowd analysis, and ESP32 status
8. Serves the web dashboard
"""

import argparse
import asyncio
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
import logging
import os
import socket
import sys
import time

import cv2
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
import numpy as np
import torch
from ultralytics import YOLO
import uvicorn

# Ensure src/ is on sys.path for local module imports
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from esp32_manager import esp32_manager, CROWD_PRESETS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
ROWS = 3
COLS = 4
CONF_THRESHOLD = 0.25


def get_all_local_ips() -> list[str]:
    """Retrieve all local IPv4 addresses on host network adapters."""
    ips = set()
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ":" not in ip and not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass
    return sorted(list(ips))


class AnalysisServer:
    def __init__(self):
        self.model = None
        self.running = False
        self.clients = set()
        self.recent_alerts = deque(maxlen=100)
        self.stats = {
            "total_people": 0,
            "fps": 0.0,
            "density_classification": "low",
            "grid": {"rows": ROWS, "cols": COLS, "zones": []},
            "alerts": [],
            "esp32": {
                "connected": False,
                "client_ip": None,
                "server_port": 8002,
                "is_streaming": False,
                "current_audio": None,
                "last_button_event": None,
            },
        }
        self.gopro_url = "http://localhost:8081/capture"
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "yolov8n.pt"
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.capture_interval = 0.5
        self.bg_task = None

    def load_model(self):
        logger.info(f"Loading YOLO model {self.model_path} on {self.device}")
        self.model = YOLO(self.model_path)
        self.model.to(self.device)

    async def analysis_loop(self):
        self.running = True
        async with httpx.AsyncClient() as client:
            while self.running:
                start_time = time.time()
                try:
                    resp = await client.get(self.gopro_url, timeout=2.0)
                    resp.raise_for_status()

                    image_array = np.frombuffer(resp.content, dtype=np.uint8)
                    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                    if frame is not None:
                        await self.process_frame(frame)
                except Exception as e:
                    logger.debug(f"Frame fetch/process idle: {e}")

                elapsed = time.time() - start_time
                self.stats["fps"] = round(1.0 / elapsed, 1) if elapsed > 0 else 0.0

                # Refresh ESP32 status inside stats
                self.stats["esp32"] = esp32_manager.get_status()

                await self.broadcast_results()

                sleep_time = max(0, self.capture_interval - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

    async def process_frame(self, frame):
        # Run YOLO inference (class 0 = person)
        results = self.model(frame, classes=[0], conf=CONF_THRESHOLD, imgsz=640, verbose=False)[0]

        height, width = frame.shape[:2]
        zone_width = width / COLS
        zone_height = height / ROWS

        counts = [0] * (ROWS * COLS)

        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            c = int(cx // zone_width)
            r = int(cy // zone_height)

            c = min(c, COLS - 1)
            r = min(r, ROWS - 1)

            zone_idx = r * COLS + c
            counts[zone_idx] += 1

        total_people = sum(counts)
        avg_people = total_people / (ROWS * COLS)

        overall_density = "low"
        if avg_people >= 20:
            overall_density = "critical"
        elif avg_people >= 10:
            overall_density = "elevated"
        elif avg_people >= 3:
            overall_density = "moderate"

        zones = []
        new_alerts = []

        for idx, count in enumerate(counts):
            r = idx // COLS
            c = idx % COLS
            zone_id = idx + 1

            density = "low"
            if count > 25:
                density = "critical"
            elif count >= 16:
                density = "high"
            elif count >= 6:
                density = "medium"

            zones.append({
                "zone_id": zone_id,
                "row": r,
                "col": c,
                "count": count,
                "density": density
            })

            if density in ["high", "critical"]:
                level = "warning" if density == "high" else "critical"
                alert = {
                    "level": level,
                    "zone_id": zone_id,
                    "message": f"Zone {zone_id}: {density.title()} density ({count} people)",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "gps": None,
                    "count": count
                }
                new_alerts.append(alert)
                self.recent_alerts.append(alert)

        self.stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_people": total_people,
            "grid": {
                "rows": ROWS,
                "cols": COLS,
                "zones": zones
            },
            "alerts": new_alerts,
            "fps": self.stats.get("fps", 0.0),
            "source": "gopro",
            "density_classification": overall_density,
            "esp32": esp32_manager.get_status(),
        }

    async def broadcast_results(self):
        if not self.clients:
            return
        message = json.dumps(self.stats)
        disconnected = set()
        for client in self.clients:
            try:
                await client.send_text(message)
            except Exception:
                disconnected.add(client)
        for client in disconnected:
            self.clients.remove(client)


server = AnalysisServer()


def on_esp32_physical_button():
    """Triggered when the physical button (GPIO 14) on the ESP32 is pressed."""
    logger.info("🔘 Physical button event received from ESP32 (GPIO 14)")
    btn_alert = {
        "level": "warning",
        "zone_id": "HW-BTN",
        "message": "Physical Button Alert on ESP32 (GPIO 14)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gps": None,
        "count": server.stats.get("total_people", 0)
    }
    server.recent_alerts.append(btn_alert)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    server.load_model()
    # Start wireless TCP server for ESP32 on port 8002
    esp32_manager.start(on_button_press=on_esp32_physical_button)
    # Start analysis loop
    server.bg_task = asyncio.create_task(server.analysis_loop())
    yield
    # Shutdown
    server.running = False
    if server.bg_task:
        server.bg_task.cancel()
    esp32_manager.stop()


app = FastAPI(title="Analysis & Dashboard Server with ESP32 Integration", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": server.model is not None,
        "device": server.device,
        "esp32_connected": esp32_manager.is_esp32_connected(),
    }


@app.get("/stats")
def get_stats():
    return server.stats


@app.get("/drone/status")
def drone_status():
    return {"gps": None, "altitude": None, "battery": None, "flight_mode": None, "status": "not_connected"}


@app.get("/network/info")
def get_network_info():
    """Returns local network adapter IPs and ESP32 connection guidelines."""
    local_ips = get_all_local_ips()
    return {
        "laptop_ips": local_ips,
        "esp32_port": esp32_manager.port,
        "esp32_connected": esp32_manager.is_esp32_connected(),
        "esp32_client": esp32_manager.get_status().get("client_ip"),
        "note": "Set LAPTOP_IP in ESP32 Arduino code to your Wi-Fi/Hotspot adapter IPv4 from the list above.",
    }


# ── ESP32 Hardware & Audio Control Endpoints ─────────────────────────

@app.get("/esp32/status")
def get_esp32_status():
    return esp32_manager.get_status()


@app.post("/esp32/play")
async def play_esp32_audio(req: Request):
    """
    Play sound signal or speech announcement on the ESP32 speaker.
    Body JSON options:
      {"type": "preset", "preset": "siren" | "chime" | "alarm" | "beep" | "disperse" | "warning" | "evacuate"}
      {"type": "tts", "text": "...", "lang": "en"}
    """
    try:
        body = await req.json()
    except Exception:
        raise HTTPException(400, detail="Invalid JSON body")

    sound_type = body.get("type", "preset")

    if sound_type == "preset":
        preset_key = body.get("preset", "siren")
        ok, msg = esp32_manager.play_preset(preset_key)
        if not ok:
            raise HTTPException(400, detail=msg)
        return {"status": "ok", "message": msg}

    elif sound_type == "tts":
        text = body.get("text", "")
        lang = body.get("lang", "en")
        ok, msg = esp32_manager.play_custom_tts(text, lang=lang)
        if not ok:
            raise HTTPException(400, detail=msg)
        return {"status": "ok", "message": msg}

    raise HTTPException(400, detail="Invalid sound type. Use 'preset' or 'tts'.")


@app.post("/esp32/stop")
def stop_esp32_audio():
    esp32_manager.stop_audio()
    return {"status": "ok", "message": "Audio stream stopped"}


# ── WebSockets ───────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    server.clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        server.clients.remove(websocket)


# ── Dashboard Static Files ───────────────────────────────────────────

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dashboard_dir = os.path.join(base_dir, "dashboard")

if os.path.exists(dashboard_dir):
    app.mount("/dashboard_static", StaticFiles(directory=dashboard_dir), name="dashboard")

    @app.get("/")
    def serve_index():
        index_path = os.path.join(dashboard_dir, "index.html")
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse(content="<h1>Dashboard index.html not found</h1>")
else:
    @app.get("/")
    def no_dashboard():
        return HTMLResponse(content=f"<h1>Dashboard directory not found at {dashboard_dir}</h1>")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analysis & Dashboard Server with ESP32 Hardware Integration")
    parser.add_argument("--port", type=int, default=8082, help="HTTP dashboard port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host bind IP")
    parser.add_argument("--gopro-url", type=str, default="http://localhost:8081/capture", help="GoPro frame URL")
    parser.add_argument("--model-path", type=str, default=None, help="Path to YOLO model (default: yolov8n.pt)")
    parser.add_argument("--interval", type=float, default=0.5, help="Analysis interval in seconds")
    parser.add_argument("--esp32-port", type=int, default=8002, help="ESP32 TCP server port (default: 8002)")

    args = parser.parse_args()

    server.gopro_url = args.gopro_url
    if args.model_path is not None:
        server.model_path = args.model_path
    server.capture_interval = args.interval
    esp32_manager.port = args.esp32_port

    logger.info("=" * 65)
    logger.info("  AI Analysis & Dashboard Server")
    logger.info("=" * 65)
    logger.info(f"  Dashboard URL: http://localhost:{args.port}")
    logger.info(f"  ESP32 TCP Port: {args.esp32_port} (Pin 25 DAC, Pin 14 Button)")
    logger.info(f"  GoPro Source:  {args.gopro_url}")
    logger.info(f"  Local IPs:     {', '.join(get_all_local_ips())}")
    logger.info("=" * 65)

    uvicorn.run(app, host=args.host, port=args.port)
