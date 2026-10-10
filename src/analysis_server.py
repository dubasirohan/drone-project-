"""
analysis_server.py — AI Analysis & Dashboard Server

Responsibilities:
1. Grabs frames from gopro_client.py (HTTP GET /capture)
2. Runs YOLOv8n person detection
3. Grid-based zone counting (3 rows x 4 cols)
4. Density classification per zone
5. Alert generation for high-density zones
6. WebSocket broadcast to dashboard clients
7. Serves the web dashboard
"""

import argparse
import asyncio
import cv2
import httpx
import json
import logging
import numpy as np
import os
import time
from collections import deque
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import torch
import uvicorn
from ultralytics import YOLO
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
ROWS = 3
COLS = 4
CONF_THRESHOLD = 0.25

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
            "grid": {"rows": ROWS, "cols": COLS, "zones": []}
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
                    
                    # decode image
                    image_array = np.frombuffer(resp.content, dtype=np.uint8)
                    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        await self.process_frame(frame)
                except Exception as e:
                    logger.error(f"Error fetching/processing frame: {e}")
                
                elapsed = time.time() - start_time
                self.stats["fps"] = round(1.0 / elapsed, 1) if elapsed > 0 else 0.0
                
                await self.broadcast_results()
                
                sleep_time = max(0, self.capture_interval - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

    async def process_frame(self, frame):
        # Run YOLO inference
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
            "density_classification": overall_density
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    server.load_model()
    server.bg_task = asyncio.create_task(server.analysis_loop())
    yield
    # Shutdown
    server.running = False
    if server.bg_task:
        server.bg_task.cancel()

app = FastAPI(title="Analysis & Dashboard Server", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": server.model is not None, "device": server.device}

@app.get("/stats")
def get_stats():
    return server.stats

@app.get("/drone/status")
def drone_status():
    return {"gps": None, "altitude": None, "battery": None, "flight_mode": None, "status": "not_connected"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    server.clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        server.clients.remove(websocket)

# Serve dashboard if it exists, otherwise provide fallback
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
    parser = argparse.ArgumentParser(description="Analysis & Dashboard Server")
    parser.add_argument("--port", type=int, default=8082)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--gopro-url", type=str, default="http://localhost:8081/capture")
    parser.add_argument("--model-path", type=str, default=None, help="Path to YOLO model (default: yolov8n.pt in project root)")
    parser.add_argument("--interval", type=float, default=0.5)
    
    args = parser.parse_args()
    
    # Apply CLI args
    server.gopro_url = args.gopro_url
    if args.model_path is not None:
        server.model_path = args.model_path
    server.capture_interval = args.interval
    
    logger.info(f"Starting Analysis Server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
