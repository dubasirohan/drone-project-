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
<<<<<<< Updated upstream
import json
import logging
import os
=======
import os
os.environ.setdefault("YOLO_AUTOINSTALL", "0")  # Block ultralytics auto-dep-install (lap etc) at runtime
import json
import logging
from pathlib import Path
>>>>>>> Stashed changes
import socket
import sys
import time

<<<<<<< Updated upstream
import cv2
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
=======
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import cv2
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
CONF_THRESHOLD = 0.25
=======
CONF_THRESHOLD = 0.035
INFERENCE_IMGSZ = 960
NUM_THREADS = 8


class AerialTracker:
    """
    Robust Multi-Object Aerial Tracker for drone surveillance.
    Unlike standard ByteTrack which drops 70-100% of aerial targets due to strict
    2-frame IoU>0.7 confirmation gates, AerialTracker guarantees:
    1. 100% of YOLO-detected people are preserved, displayed, and counted in the 3x4 grid.
    2. Persistent track IDs are assigned and tracked across successive frames using IoU & distance.
    3. Retains lost targets over short occlusions (up to 30 frames).
    4. Applies coordinate smoothing to eliminate visual jitter.
    """
    def __init__(self, max_lost: int = 30):
        self.next_id = 1
        self.tracks = {}  # tid -> {'bbox': [x1, y1, x2, y2], 'lost': int}
        self.max_lost = max_lost

    def update(self, detections: list) -> list:
        """
        Args: detections: list of [x1, y1, x2, y2, conf]
        Returns: list of [x1, y1, x2, y2, conf, track_id]
        """
        new_tracks = {}
        unmatched_dets = list(range(len(detections)))
        tracked_out = []

        # 1. Match active existing tracks to closest detections
        for tid, tinfo in self.tracks.items():
            tx1, ty1, tx2, ty2 = tinfo['bbox']
            tcx, tcy = (tx1 + tx2) / 2.0, (ty1 + ty2) / 2.0
            tw, th = max(1.0, tx2 - tx1), max(1.0, ty2 - ty1)

            best_match = None
            best_dist = max(80.0, (tw + th) * 1.5)  # dynamic search radius

            for d_idx in unmatched_dets:
                dx1, dy1, dx2, dy2, _ = detections[d_idx]
                dcx, dcy = (dx1 + dx2) / 2.0, (dy1 + dy2) / 2.0
                dist = ((tcx - dcx)**2 + (tcy - dcy)**2)**0.5

                # IoU overlap calculation
                ix1, iy1 = max(tx1, dx1), max(ty1, dy1)
                ix2, iy2 = min(tx2, dx2), min(ty2, dy2)
                inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
                union = (tw * th) + ((dx2 - dx1) * (dy2 - dy1)) - inter
                iou = inter / max(1.0, union)
                effective_dist = dist * (1.0 - 0.6 * iou)

                if effective_dist < best_dist:
                    best_dist = effective_dist
                    best_match = d_idx

            if best_match is not None:
                d = detections[best_match]
                # Smooth box coordinates (75% current + 25% previous)
                smoothed_box = [
                    round(0.75 * d[0] + 0.25 * tx1, 2),
                    round(0.75 * d[1] + 0.25 * ty1, 2),
                    round(0.75 * d[2] + 0.25 * tx2, 2),
                    round(0.75 * d[3] + 0.25 * ty2, 2)
                ]
                new_tracks[tid] = {'bbox': smoothed_box, 'lost': 0}
                tracked_out.append(smoothed_box + [d[4], tid])
                unmatched_dets.remove(best_match)
            elif tinfo['lost'] < self.max_lost:
                new_tracks[tid] = {'bbox': tinfo['bbox'], 'lost': tinfo['lost'] + 1}

        # 2. Assign fresh IDs to newly appeared detections — NEVER DISCARD A DETECTION
        for d_idx in unmatched_dets:
            tid = self.next_id
            self.next_id += 1
            d = detections[d_idx]
            new_tracks[tid] = {'bbox': d[:4], 'lost': 0}
            tracked_out.append(d[:4] + [d[4], tid])

        self.tracks = new_tracks
        return tracked_out

    def reset(self):
        self.tracks.clear()
        self.next_id = 1
>>>>>>> Stashed changes


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
<<<<<<< Updated upstream
=======
            "source": "gopro",
            "scenario": None,
            "active_clip": None,
            "auto_cycle": False,
            "detections": [],
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
        self.gopro_health_url = "http://localhost:8081/health"
>>>>>>> Stashed changes
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "yolov8n.pt"
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
<<<<<<< Updated upstream
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
=======
        self.tracker = AerialTracker()
        self.capture_interval = 1.2  # kept for compatibility, no longer used as a sleep cap
        self.bg_task = None
        self._health_poll_ticks = 0
        self._fps_times = []  # rolling timestamps of completed YOLO inferences

    @property
    def gopro_base_url(self) -> str:
        return self.gopro_url.rsplit("/", 1)[0]

    def load_model(self):
        import torch
        torch.set_num_threads(NUM_THREADS)
        logger.info(f"Loading YOLO model {self.model_path} on {self.device} (threads={NUM_THREADS})")
        self.model = YOLO(self.model_path)
        self.model.to(self.device)
        # Warmup pass so first real inference is fast
        _dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        self.model(_dummy, classes=[0], conf=CONF_THRESHOLD, imgsz=INFERENCE_IMGSZ, verbose=False)
        logger.info("YOLOv8 + AerialTracker ready for real-time aerial inference.")

    def reset_tracker(self):
        """Reset tracker state so new scenes/clips start fresh without ID churn."""
        self.tracker.reset()
        self.stats["detections"] = []

    async def analysis_loop(self):
        import concurrent.futures
        self.running = True
        loop = asyncio.get_event_loop()
        # Single worker: prevents queue pile-up — only one YOLO inference at a time
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        last_source = self.stats.get("source")
        last_scenario_id = self.stats.get("scenario", {}).get("id") if self.stats.get("scenario") else None
        last_clip_id = self.stats.get("active_clip", {}).get("id") if self.stats.get("active_clip") else None

        async with httpx.AsyncClient() as client:
            while self.running:
                try:
                    # Periodically sync camera health & scenario/clip state
                    self._health_poll_ticks += 1
                    if self._health_poll_ticks % 5 == 0:
                        try:
                            h_resp = await client.get(self.gopro_health_url, timeout=0.8)
                            if h_resp.status_code == 200:
                                h_data = h_resp.json()
                                cur_src = h_data.get("source", self.stats["source"])
                                cur_sc = h_data.get("scenario")
                                cur_clip = h_data.get("active_clip")
                                cur_sc_id = cur_sc.get("id") if cur_sc else None
                                cur_clip_id = cur_clip.get("id") if cur_clip else None

                                if cur_src != last_source or cur_sc_id != last_scenario_id or cur_clip_id != last_clip_id:
                                    logger.info(f"Source/scene changed: src={cur_src}, sc={cur_sc_id}, clip={cur_clip_id} -> Resetting tracker")
                                    self.reset_tracker()
                                    last_source = cur_src
                                    last_scenario_id = cur_sc_id
                                    last_clip_id = cur_clip_id

                                self.stats["source"] = cur_src
                                self.stats["scenario"] = cur_sc
                                self.stats["active_clip"] = cur_clip
                                self.stats["auto_cycle"] = h_data.get("auto_cycle", False)
                        except Exception:
                            pass

>>>>>>> Stashed changes
                    resp = await client.get(self.gopro_url, timeout=2.0)
                    resp.raise_for_status()

                    image_array = np.frombuffer(resp.content, dtype=np.uint8)
                    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                    if frame is not None:
<<<<<<< Updated upstream
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

=======
                        # Run tracker in thread — awaiting ensures stats are fresh before broadcast
                        await loop.run_in_executor(executor, self._process_frame_sync, frame)
                        # Refresh ESP32 status and broadcast immediately after inference
                        self.stats["esp32"] = esp32_manager.get_status()
                        await self.broadcast_results()

                except Exception as e:
                    logger.debug(f"Frame fetch/process error: {e}")
                    # Brief pause on error to avoid hammering the camera server
                    await asyncio.sleep(0.2)

    def _detect_people(self, frame) -> list:
        """
        Detect pedestrians using YOLOv8 with adaptive aerial tiling.
        Returns list of [x1, y1, x2, y2, conf] in pixel coordinates.
        """
        h, w = frame.shape[:2]
        is_scenario = (self.stats.get("source") == "scenario")
        active_clip_id = self.stats.get("active_clip", {}).get("id") if self.stats.get("active_clip") else None

        # 1. Primary full-frame inference
        try:
            res = self.model(
                frame,
                classes=[0],
                conf=CONF_THRESHOLD,
                imgsz=INFERENCE_IMGSZ,
                verbose=False
            )[0]
            raw_dets = []
            for b in res.boxes:
                x1, y1, x2, y2 = b.xyxy[0].tolist()
                conf_val = float(b.conf[0])
                raw_dets.append([x1, y1, x2, y2, conf_val])
        except Exception as e:
            logger.error(f"Full-frame YOLO error: {e}")
            raw_dets = []

        # 2. High-altitude aerial tiling:
        # If the active clip is high-altitude nadir (clip_5 / clip_6) or detections < 4 on video,
        # run a 3x3 overlapping crop grid so tiny (4-15px) pedestrians are clearly resolved.
        need_tiling = (
            not is_scenario and
            (active_clip_id in ("clip_5", "clip_6") or len(raw_dets) < 4)
        )

        if need_tiling:
            tile_h, tile_w = int(h * 0.45), int(w * 0.45)
            step_y = max(1, (h - tile_h) // 2)
            step_x = max(1, (w - tile_w) // 2)
            tile_coords = []
            for r in range(3):
                for c in range(3):
                    tile_coords.append((c * step_x, r * step_y))

            crops = [frame[y:y+tile_h, x:x+tile_w] for x, y in tile_coords]
            try:
                batch_res = self.model(crops, classes=[0], conf=0.03, imgsz=640, verbose=False)
                for (tx, ty), b_res in zip(tile_coords, batch_res):
                    for b in b_res.boxes:
                        bx1, by1, bx2, by2 = b.xyxy[0].tolist()
                        bconf = float(b.conf[0])
                        gx1, gy1, gx2, gy2 = bx1 + tx, by1 + ty, bx2 + tx, by2 + ty

                        # Proximity suppression against existing detections
                        overlap = False
                        cx1, cy1 = (gx1 + gx2) / 2.0, (gy1 + gy2) / 2.0
                        for ex in raw_dets:
                            cx2, cy2 = (ex[0] + ex[2]) / 2.0, (ex[1] + ex[3]) / 2.0
                            if abs(cx1 - cx2) < 18 and abs(cy1 - cy2) < 18:
                                overlap = True
                                break
                        if not overlap:
                            raw_dets.append([gx1, gy1, gx2, gy2, bconf])
            except Exception as e:
                logger.error(f"Tile inference error: {e}")

        return raw_dets

    def _process_frame_sync(self, frame):
        """Synchronous YOLO + AerialTracker inference running in ThreadPoolExecutor."""
        t0 = time.time()
        is_scenario = (self.stats.get("source") == "scenario")

        # 1. Run detection
        raw_dets = self._detect_people(frame)

        # 2. Track detections
        if is_scenario:
            # Static scenarios don't need temporal smoothing
            tracked = [d[:4] + [d[4], idx + 1] for idx, d in enumerate(raw_dets)]
        else:
            # AerialTracker maintains persistent IDs and smooths coordinates across frames
            tracked = self.tracker.update(raw_dets)

        # 3. Update stats, 3x4 grid, density, and alerts
        self._update_stats_from_tracked(tracked, frame)

        # 4. Rolling FPS measurement
        now = time.time()
        self._fps_times.append(now)
        self._fps_times = [t for t in self._fps_times if now - t <= 5.0]
        if len(self._fps_times) > 1:
            span = max(1.0, now - self._fps_times[0])
            self.stats["fps"] = round(len(self._fps_times) / span, 1)
        else:
            self.stats["fps"] = 0.0

        logger.debug(
            f"Inference: {len(tracked)} tracked ({time.time()-t0:.2f}s, fps={self.stats['fps']})"
        )

    async def process_frame(self, frame):
        """Async wrapper kept for compatibility."""
        self._process_frame_sync(frame)

    def _update_stats_from_tracked(self, tracked, frame):
>>>>>>> Stashed changes
        height, width = frame.shape[:2]
        zone_width = width / COLS
        zone_height = height / ROWS

        counts = [0] * (ROWS * COLS)
<<<<<<< Updated upstream

        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            c = int(cx // zone_width)
            r = int(cy // zone_height)

            c = min(c, COLS - 1)
            r = min(r, ROWS - 1)
=======
        detections = []

        for item in tracked:
            x1, y1, x2, y2, conf, track_id = item
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            c = max(0, min(int(cx // zone_width), COLS - 1))
            r = max(0, min(int(cy // zone_height), ROWS - 1))
>>>>>>> Stashed changes

            zone_idx = r * COLS + c
            counts[zone_idx] += 1

<<<<<<< Updated upstream
        total_people = sum(counts)
        avg_people = total_people / (ROWS * COLS)

        overall_density = "low"
        if avg_people >= 20:
            overall_density = "critical"
        elif avg_people >= 10:
            overall_density = "elevated"
        elif avg_people >= 3:
            overall_density = "moderate"
=======
            detections.append([
                round(x1 / width, 4),
                round(y1 / height, 4),
                round(x2 / width, 4),
                round(y2 / height, 4),
                round(conf, 3),
                track_id
            ])

        total_people = sum(counts)
>>>>>>> Stashed changes

        zones = []
        new_alerts = []

        for idx, count in enumerate(counts):
            r = idx // COLS
            c = idx % COLS
            zone_id = idx + 1

<<<<<<< Updated upstream
            density = "low"
            if count > 25:
                density = "critical"
            elif count >= 16:
                density = "high"
            elif count >= 6:
                density = "medium"
=======
            if count >= 9:
                density = "critical"
            elif count >= 5:
                density = "high"
            elif count >= 2:
                density = "medium"
            else:
                density = "low"
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
        self.stats = {
=======
        if total_people >= 28 or any(z["density"] == "critical" for z in zones):
            overall_density = "critical"
        elif total_people >= 16 or any(z["density"] == "high" for z in zones):
            overall_density = "high"
        elif total_people >= 6 or any(z["density"] == "medium" for z in zones):
            overall_density = "moderate"
        else:
            overall_density = "low"

        self.stats.update({
>>>>>>> Stashed changes
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_people": total_people,
            "grid": {
                "rows": ROWS,
                "cols": COLS,
                "zones": zones
            },
            "alerts": new_alerts,
<<<<<<< Updated upstream
            "fps": self.stats.get("fps", 0.0),
            "source": "gopro",
            "density_classification": overall_density,
            "esp32": esp32_manager.get_status(),
        }
=======
            "density_classification": overall_density,
            "detections": detections,
        })
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    logger.info("🔘 Physical button event received from ESP32 (GPIO 14)")
=======
    logger.info("[BUTTON] Physical button event received from ESP32 (GPIO 14)")
>>>>>>> Stashed changes
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


<<<<<<< Updated upstream
=======
# ── Scenario & Camera Feed Proxy Endpoints ───────────────────────────

@app.get("/scenarios")
async def get_scenarios():
    """Proxy scenarios list from camera server or fallback to local file."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{server.gopro_base_url}/scenarios", timeout=2.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

    scenarios_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "test", "scenarios", "scenarios.json"
    )
    if os.path.exists(scenarios_file):
        import json
        with open(scenarios_file, "r", encoding="utf-8") as f:
            sc_list = json.load(f)
        return {
            "status": "ok",
            "scenarios": sc_list,
            "active_scenario": server.stats.get("scenario"),
            "auto_cycle": server.stats.get("auto_cycle", False),
        }
    return {"status": "error", "scenarios": []}


@app.post("/scenario")
async def select_scenario(id: str):
    """Proxy scenario selection to camera server."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{server.gopro_base_url}/scenario", params={"id": id}, timeout=2.5)
            if resp.status_code == 200:
                data = resp.json()
                server.stats["source"] = "scenario"
                server.stats["scenario"] = data.get("scenario")
                server.stats["auto_cycle"] = False
                server.reset_tracker()
                return data
            raise HTTPException(resp.status_code, detail=resp.text)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(502, detail=f"GoPro camera server unreachable: {e}")


@app.post("/scenario/cycle")
async def toggle_scenario_cycle(enabled: bool = None, interval: float = None):
    """Proxy auto-cycle toggle to camera server."""
    params = {}
    if enabled is not None:
        params["enabled"] = str(enabled).lower()
    if interval is not None:
        params["interval"] = str(interval)
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{server.gopro_base_url}/scenario/cycle", params=params, timeout=2.5)
            if resp.status_code == 200:
                data = resp.json()
                server.stats["auto_cycle"] = data.get("auto_cycle", False)
                return data
            raise HTTPException(resp.status_code, detail=resp.text)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(502, detail=f"GoPro camera server unreachable: {e}")


@app.post("/source")
async def switch_source(req: Request, source: str = None):
    """Proxy source switch to camera server."""
    if not source:
        try:
            body = await req.json()
            source = body.get("source")
        except Exception:
            pass
    if not source:
        raise HTTPException(400, detail="Missing 'source' parameter or JSON body")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{server.gopro_base_url}/source", params={"source": source}, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                server.stats["source"] = data.get("source", source)
                server.reset_tracker()
                return data
            raise HTTPException(resp.status_code, detail=resp.text)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(502, detail=f"GoPro camera server unreachable: {e}")


@app.get("/clips")
async def get_clips():
    """Proxy video clips list from camera server."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{server.gopro_base_url}/clips", timeout=2.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    return {"status": "error", "clips": [], "active_clip": server.stats.get("active_clip")}


@app.post("/clip")
async def select_clip(id: str):
    """Proxy video clip selection to camera server."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{server.gopro_base_url}/clip", params={"id": id}, timeout=2.5)
            if resp.status_code == 200:
                data = resp.json()
                server.stats["source"] = "sample"
                server.stats["active_clip"] = data.get("clip")
                server.stats["scenario"] = None
                server.stats["auto_cycle"] = False
                server.reset_tracker()
                return data
            raise HTTPException(resp.status_code, detail=resp.text)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(502, detail=f"GoPro camera server unreachable: {e}")


@app.get("/preview")
@app.get("/stream")
async def proxy_preview():
    """Proxy MJPEG stream from camera server for zero-CORS browser delivery."""
    async def stream_generator():
        client = httpx.AsyncClient(timeout=None)
        try:
            async with client.stream("GET", f"{server.gopro_base_url}/preview") as r:
                async for chunk in r.aiter_bytes():
                    yield chunk
        except Exception:
            pass
        finally:
            await client.aclose()

    return StreamingResponse(
        stream_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )



>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
    server.gopro_health_url = f"{server.gopro_base_url}/health"
>>>>>>> Stashed changes
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
