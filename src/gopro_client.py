"""
gopro_client.py — GoPro & Camera Handler running on Laptop.

Connection Modes:
  1. "gopro"   — Direct WiFi AP mode (GoPro at 10.5.5.9, lowest latency ~100ms)
                 Requires: laptop WiFi → GoPro's own WiFi network
                 Internet: use USB tethering from phone as second adapter
  2. "usb"     — USB Webcam mode via GoPro Webcam Utility (best latency ~50ms)
                 Requires: USB-C cable + GoPro Webcam desktop app installed
                 Internet: WiFi stays free for internet
  3. "hotspot" — GoPro on external WiFi (phone hotspot) via STA mode (~200ms)
                 Requires: finding GoPro's DHCP IP on the hotspot subnet
                 Internet: same hotspot provides internet
  4. "webcam"  — Laptop's built-in webcam (fallback for testing)

Endpoints:
  GET  /capture   → Latest frame as high-quality JPEG (for AI analysis)
  GET  /preview   → MJPEG live stream (for dashboard browser)
  GET  /health    → Status JSON
  POST /source    → Switch between sources: gopro | usb | hotspot | webcam
"""
import argparse
import asyncio
<<<<<<< Updated upstream
=======
import json
>>>>>>> Stashed changes
import os
import socket
import struct
import subprocess
<<<<<<< Updated upstream
=======
import sys
>>>>>>> Stashed changes
import threading
import time
from contextlib import asynccontextmanager

<<<<<<< Updated upstream
=======
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

>>>>>>> Stashed changes
import cv2
import numpy as np
import requests
import uvicorn
<<<<<<< Updated upstream
from fastapi import FastAPI, HTTPException, Response
=======
from fastapi import FastAPI, HTTPException, Response, Request
>>>>>>> Stashed changes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# ── Low-latency FFMPEG tuning ────────────────────────────────────────
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "fflags;nobuffer|flags;low_delay|framedrop;1"
)

GOPRO_IP = os.getenv("GOPRO_IP", "10.5.5.9")
DEFAULT_SAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "test", "clip.mp4"
)
<<<<<<< Updated upstream
VALID_SOURCES = ("gopro", "usb", "hotspot", "webcam", "sample")
=======
DEFAULT_SCENARIOS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "test", "scenarios", "scenarios.json"
)
VALID_SOURCES = ("gopro", "usb", "hotspot", "webcam", "sample", "scenario", "cycle")

>>>>>>> Stashed changes


# ── Network Utilities ────────────────────────────────────────────────

def get_local_ip() -> str:
    """Get this machine's IP on the current network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "0.0.0.0"


def scan_for_gopro(subnet: str = None, timeout: float = 1.0) -> str | None:
    """
    Scan the local subnet for a GoPro by trying the HTTP API on port 8080.
    Returns the GoPro's IP if found, else None.
    """
    if subnet is None:
        local_ip = get_local_ip()
        # Derive subnet from local IP (e.g., 192.168.43.x → 192.168.43)
        parts = local_ip.split(".")
        if len(parts) != 4:
            return None
        subnet = ".".join(parts[:3])

    print(f"[gopro_client] Scanning subnet {subnet}.0/24 for GoPro...")

    found_ip = None

    def probe(ip: str):
        nonlocal found_ip
        if found_ip:
            return
        try:
            r = requests.get(
                f"http://{ip}:8080/gopro/camera/state",
                timeout=timeout,
            )
            if r.status_code == 200:
                found_ip = ip
<<<<<<< Updated upstream
                print(f"[gopro_client] ✓ Found GoPro at {ip}")
=======
                print(f"[gopro_client] [OK] Found GoPro at {ip}")
>>>>>>> Stashed changes
        except Exception:
            pass

    threads = []
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        t = threading.Thread(target=probe, args=(ip,), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=timeout + 0.5)

    return found_ip


def arp_find_gopro() -> str | None:
    """Try to find GoPro via ARP table (faster than full scan)."""
    try:
        result = subprocess.run(
            ["arp", "-a"], capture_output=True, text=True, timeout=5
        )
        # Look through ARP entries and probe each for GoPro API
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                ip_candidate = parts[0]
                # Basic IP format check
                if ip_candidate.count(".") == 3 and ip_candidate[0].isdigit():
                    try:
                        r = requests.get(
                            f"http://{ip_candidate}:8080/gopro/camera/state",
                            timeout=0.5,
                        )
                        if r.status_code == 200:
<<<<<<< Updated upstream
                            print(f"[gopro_client] ✓ Found GoPro at {ip_candidate} (via ARP)")
=======
                            print(f"[gopro_client] [OK] Found GoPro at {ip_candidate} (via ARP)")
>>>>>>> Stashed changes
                            return ip_candidate
                    except Exception:
                        pass
    except Exception:
        pass
    return None


# ── Placeholder Frame ────────────────────────────────────────────────

def create_placeholder_frame(text: str) -> np.ndarray:
    """Creates a dark slate placeholder frame with status text."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (20, 24, 33)

    for y in range(0, 480, 40):
        cv2.line(frame, (0, y), (640, y), (30, 36, 48), 1)
    for x in range(0, 640, 40):
        cv2.line(frame, (x, 0), (x, 480), (30, 36, 48), 1)

    cv2.rectangle(frame, (80, 200), (560, 280), (37, 45, 61), -1)
    cv2.rectangle(frame, (80, 200), (560, 280), (79, 70, 229), 2)

    # Word-wrap if text is long
    if len(text) > 50:
        cv2.putText(frame, text[:50], (100, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 225, 235), 1, cv2.LINE_AA)
        cv2.putText(frame, text[50:], (100, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 225, 235), 1, cv2.LINE_AA)
    else:
        cv2.putText(frame, text, (100, 245), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 225, 235), 2, cv2.LINE_AA)
    return frame


# ── Camera Streamer ──────────────────────────────────────────────────

class CameraStreamer:
    def __init__(self, gopro_ip: str = GOPRO_IP, default_source: str = "gopro",
<<<<<<< Updated upstream
                 usb_index: int = None, sample_path: str = DEFAULT_SAMPLE_PATH):
=======
                 usb_index: int = None, sample_path: str = DEFAULT_SAMPLE_PATH,
                 scenarios_path: str = DEFAULT_SCENARIOS_PATH):
>>>>>>> Stashed changes
        self.gopro_ip = gopro_ip
        self.source = default_source
        self.running = False
        self._cap: cv2.VideoCapture | None = None
        self._lock = threading.Lock()
        self._frame: np.ndarray | None = None
        self._ret = False
        self.status = "Initializing..."
        self._worker: threading.Thread | None = None
        self._keepalive_worker: threading.Thread | None = None

        # USB webcam mode settings
        self.usb_index = usb_index  # None = auto-detect

<<<<<<< Updated upstream
        # Sample video mode settings (Demo Mode)
        self.sample_path = sample_path
        self._sample_fps = 25.0
=======
        # Sample video & Demo Clips settings
        self.sample_path = sample_path
        self._sample_fps = 25.0
        self.clips = self._load_clips()
        self.active_clip: dict | None = None
        for c in self.clips:
            if os.path.abspath(c["path"]) == os.path.abspath(self.sample_path):
                self.active_clip = c
                break
        if not self.active_clip and self.clips:
            self.active_clip = self.clips[0]
            self.sample_path = self.active_clip["path"]

        # Dataset Scenario Demo settings
        self.scenarios_path = scenarios_path
        self.scenarios = self._load_scenarios()
        self.active_scenario: dict | None = None
        self.auto_cycle = False
        self.cycle_interval = 8.0  # seconds per scenario
        self.last_cycle_time = 0.0
        self.cycle_idx = 0
        self._scenario_frame: np.ndarray | None = None
>>>>>>> Stashed changes

        # Hotspot mode: discovered IP
        self._hotspot_gopro_ip: str | None = None

<<<<<<< Updated upstream
=======
    def _load_clips(self) -> list:
        """Scan clips/ and test/ for pre-recorded aerial drone footage."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clips_dir = os.path.join(base_dir, "clips")
        test_dir = os.path.join(base_dir, "test")

        discovered = []
        # 1. Main test clip (test/clip.mp4)
        main_clip = os.path.join(test_dir, "clip.mp4")
        if os.path.exists(main_clip):
            discovered.append({
                "id": "clip_main",
                "title": "Concourse Flight (Original Drone)",
                "filename": "clip.mp4",
                "path": main_clip,
                "badge": "High Density",
                "crowd_tier": "HIGH",
                "color": "#3b82f6",
                "approx_count": "37 - 45 People",
                "description": "Aerial UAV video over campus concourse with multi-person tracking."
            })

        # 2. Clips from clips/ folder
        if os.path.exists(clips_dir):
            curated = [
                {
                    "id": "clip_1",
                    "aliases": ["clip_1", "corridor", "clip_corridor"],
                    "filename": "WhatsApp Video 2026-10-16 at 6.06.13 AM.mp4",
                    "title": "Clip 1: Aerial Corridor",
                    "badge": "Active Flow",
                    "crowd_tier": "MODERATE",
                    "color": "#f59e0b",
                    "approx_count": "11 - 15 People",
                    "description": "Aerial drone viewpoint capturing pedestrian flow through urban corridor."
                },
                {
                    "id": "clip_2",
                    "aliases": ["clip_2", "walkway", "clip_walkway"],
                    "filename": "WhatsApp Video 2026-10-16 at 6.05.23 AM.mp4",
                    "title": "Clip 2: Urban Walkway",
                    "badge": "Walkway Flow",
                    "crowd_tier": "LOW",
                    "color": "#10b981",
                    "approx_count": "3 - 5 People",
                    "description": "UAV surveillance of city walkway and perimeter."
                },
                {
                    "id": "clip_3",
                    "aliases": ["clip_3", "perimeter", "clip_perimeter"],
                    "filename": "WhatsApp Video 2026-10-16 at 6.08.09 AM.mp4",
                    "title": "Clip 3: Perimeter Patrol",
                    "badge": "Perimeter",
                    "crowd_tier": "LOW",
                    "color": "#10b981",
                    "approx_count": "2 - 4 People",
                    "description": "Perimeter surveillance monitoring low-density sector."
                },
                {
                    "id": "clip_4",
                    "aliases": ["clip_4", "transit", "clip_transit"],
                    "filename": "WhatsApp Video 2026-10-16 at 6.04.43 AM.mp4",
                    "title": "Clip 4: Transit Zone",
                    "badge": "Transit",
                    "crowd_tier": "LOW",
                    "color": "#10b981",
                    "approx_count": "1 - 2 People",
                    "description": "Transit sector with sparse pedestrian movement."
                },
                {
                    "id": "clip_5",
                    "aliases": ["clip_5", "survey", "clip_survey"],
                    "filename": "WhatsApp Video 2026-10-16 at 6.08.54 AM.mp4",
                    "title": "Clip 5: Overhead Survey",
                    "badge": "Overhead",
                    "crowd_tier": "SURVEY",
                    "color": "#8b5cf6",
                    "approx_count": "Aerial Survey",
                    "description": "High-altitude aerial survey across designated sector."
                },
                {
                    "id": "clip_6",
                    "aliases": ["clip_6", "sweep", "clip_sweep"],
                    "filename": "WhatsApp Video 2026-10-16 at 6.09.34 AM.mp4",
                    "title": "Clip 6: Broad Area Sweep",
                    "badge": "Area Sweep",
                    "crowd_tier": "SURVEY",
                    "color": "#6366f1",
                    "approx_count": "Area Sweep",
                    "description": "Wide-area tactical UAV sweep across urban zone."
                },
            ]

            handled_filenames = set()
            for c in curated:
                fpath = os.path.join(clips_dir, c["filename"])
                if os.path.exists(fpath):
                    item = dict(c)
                    item["path"] = fpath
                    discovered.append(item)
                    handled_filenames.add(c["filename"].lower())

            # Also add any additional mp4 files found in clips/
            extra_idx = 7
            for fname in sorted(os.listdir(clips_dir)):
                if fname.lower().endswith(".mp4") and fname.lower() not in handled_filenames:
                    discovered.append({
                        "id": f"clip_{extra_idx}",
                        "aliases": [f"clip_{extra_idx}", fname],
                        "title": f"Clip {extra_idx}: {fname[:20]}",
                        "filename": fname,
                        "path": os.path.join(clips_dir, fname),
                        "badge": "Sample",
                        "crowd_tier": "DEMO",
                        "color": "#3b82f6",
                        "approx_count": "Demo Video",
                        "description": f"Pre-recorded drone video: {fname}"
                    })
                    extra_idx += 1

        print(f"[gopro_client] [OK] Discovered {len(discovered)} demo video clips.")
        return discovered

    def set_clip(self, clip_id: str):
        """Switch to a specific pre-recorded video clip and start looping."""
        target = None
        cid = str(clip_id).lower().strip()
        for c in self.clips:
            aliases = [a.lower() for a in c.get("aliases", [])]
            if c["id"].lower() == cid or c["filename"].lower() == cid or cid in aliases:
                target = c
                break

        if not target:
            return False, f"Clip '{clip_id}' not found."

        with self._lock:
            self._release_cap()
            self.sample_path = target["path"]
            self.active_clip = target
            self.source = "sample"
            self.active_scenario = None
            self.status = f"Switching to clip: {target['title']}..."
            self._frame = create_placeholder_frame(self.status)

        success = self._open_sample_video()
        if success:
            print(f"[gopro_client] [OK] Active clip set to: {target['title']} ({target['id']})")
            return True, target
        return False, "Failed to open video file."

    def _load_scenarios(self) -> list:
        """Load curated VisDrone scenario metadata."""
        if os.path.exists(self.scenarios_path):
            try:
                with open(self.scenarios_path, "r", encoding="utf-8") as f:
                    sc_list = json.load(f)
                    print(f"[gopro_client] [OK] Loaded {len(sc_list)} dataset demo scenarios from {self.scenarios_path}")
                    return sc_list
            except Exception as e:
                print(f"[gopro_client] Warning: Failed to load scenarios: {e}")
        return []

    def set_scenario(self, scenario_id: str):
        """Switch to a specific VisDrone crowd scenario image."""
        for sc in self.scenarios:
            if sc["id"] == scenario_id:
                p = sc.get("file_path")
                if not p or not os.path.exists(p):
                    p = os.path.join(os.path.dirname(self.scenarios_path), sc.get("dest_filename", ""))
                if os.path.exists(p):
                    img = cv2.imread(p)
                    if img is not None:
                        with self._lock:
                            self._release_cap()
                            self.source = "scenario"
                            self.active_scenario = sc
                            self._scenario_frame = img
                            self.status = f"Scenario {sc['number']}: {sc['title']} ({sc.get('crowd_tier', 'DEMO')})"
                            self._frame = img.copy()
                            self._ret = True
                        print(f"[gopro_client] [OK] Switched to Scenario {sc['number']}: {sc['title']} [{sc['id']}]")
                        return True, sc
        return False, f"Scenario '{scenario_id}' not found."

    def toggle_auto_cycle(self, enabled: bool = None, interval: float = None) -> bool:
        """Toggle or set automated cycling through demo scenarios."""
        if interval and interval > 0:
            self.cycle_interval = interval
        if enabled is not None:
            self.auto_cycle = enabled
        else:
            self.auto_cycle = not self.auto_cycle
        if self.auto_cycle:
            self.last_cycle_time = time.time()
            print(f"[gopro_client] [OK] Auto-cycle mode ENABLED ({self.cycle_interval}s interval)")
        else:
            print("[gopro_client] [X] Auto-cycle mode DISABLED")
        return self.auto_cycle

>>>>>>> Stashed changes
    def start(self):
        self.running = True
        self._worker = threading.Thread(target=self._capture_loop, daemon=True)
        self._worker.start()
        self._keepalive_worker = threading.Thread(target=self._keepalive_loop, daemon=True)
        self._keepalive_worker.start()
        return self

    def stop(self):
        self.running = False
        self._release_cap()

    def set_source(self, source: str):
<<<<<<< Updated upstream
        source = source.lower()
        if source not in VALID_SOURCES:
            return False, f"Source must be one of: {', '.join(VALID_SOURCES)}"
        with self._lock:
            self.source = source
            self._release_cap()
            self._hotspot_gopro_ip = None
            self.status = f"Switching to {source}..."
=======
        src = source.lower().strip()
        # Direct scenario matching
        if src.startswith("scenario:"):
            sc_id = src.split(":", 1)[1]
            ok, res = self.set_scenario(sc_id)
            if ok:
                return True, f"scenario:{sc_id}"
        elif any(s["id"].lower() == src for s in self.scenarios):
            ok, res = self.set_scenario(src)
            if ok:
                return True, f"scenario:{src}"
        # Direct clip matching
        elif src.startswith("clip:"):
            clip_id = src.split(":", 1)[1]
            ok, res = self.set_clip(clip_id)
            if ok:
                return True, f"clip:{clip_id}"
        elif any(c["id"].lower() == src for c in self.clips):
            ok, res = self.set_clip(src)
            if ok:
                return True, f"clip:{src}"
        elif src == "cycle":
            self.toggle_auto_cycle(True)
            return True, "cycle"

        if src not in VALID_SOURCES:
            valid_opts = list(VALID_SOURCES) + [s["id"] for s in self.scenarios] + [c["id"] for c in self.clips]
            return False, f"Source must be one of: {', '.join(valid_opts)}"

        with self._lock:
            self.source = src
            self._release_cap()
            self._hotspot_gopro_ip = None
            if src != "scenario":
                self.active_scenario = None
            self.status = f"Switching to {src}..."
>>>>>>> Stashed changes
            self._frame = create_placeholder_frame(self.status)
        return True, self.source

    def read_frame(self) -> tuple[bool, np.ndarray | None]:
        with self._lock:
            if self._frame is None:
                return True, create_placeholder_frame(self.status)
            return self._ret, self._frame

    @property
    def active_gopro_ip(self) -> str:
        """Return the GoPro IP currently being used (direct or discovered)."""
        if self.source == "hotspot" and self._hotspot_gopro_ip:
            return self._hotspot_gopro_ip
        return self.gopro_ip

    def _release_cap(self):
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    # ── Source openers ────────────────────────────────────────────

    def _open_webcam(self) -> bool:
        """Open the laptop's built-in webcam."""
        print("[gopro_client] Opening laptop webcam (index 0)...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self._cap = cap
            self.status = "Webcam Active"
<<<<<<< Updated upstream
            print("[gopro_client] ✓ Webcam opened.")
=======
            print("[gopro_client] [OK] Webcam opened.")
>>>>>>> Stashed changes
            return True
        self.status = "Webcam not found"
        return False

    def _open_usb_gopro(self) -> bool:
        """
        Open GoPro via USB webcam mode.
        Requires: GoPro Webcam Utility running + USB-C cable connected.
        The GoPro appears as a standard UVC device.
        """
        print("[gopro_client] Opening GoPro USB webcam...")

        if self.usb_index is not None:
            # User specified an exact device index
            indices_to_try = [self.usb_index]
        else:
            # Auto-detect: try indices 0-4
            # On Windows, built-in webcam is usually 0, GoPro is 1+
            indices_to_try = [1, 2, 0, 3, 4]

        for idx in indices_to_try:
            # Use MSMF on Windows for best GoPro Webcam Utility compatibility
            backend = cv2.CAP_MSMF if os.name == "nt" else cv2.CAP_ANY
            cap = cv2.VideoCapture(idx, backend)
            if cap.isOpened():
                # Try to set 1080p — GoPro webcam supports this
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                cap.set(cv2.CAP_PROP_FPS, 30)
                # Read a test frame to confirm it's real
                ret, test = cap.read()
                if ret and test is not None:
                    self._cap = cap
                    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    self.status = f"USB GoPro Active (dev {idx}, {actual_w}x{actual_h})"
<<<<<<< Updated upstream
                    print(f"[gopro_client] ✓ USB webcam opened: device {idx} at {actual_w}x{actual_h}")
=======
                    print(f"[gopro_client] [OK] USB webcam opened: device {idx} at {actual_w}x{actual_h}")
>>>>>>> Stashed changes
                    return True
                cap.release()

        self.status = "USB GoPro not found — is GoPro Webcam Utility running?"
<<<<<<< Updated upstream
        print("[gopro_client] ✗ No USB GoPro webcam device found.")
        print("  → Make sure the GoPro Webcam desktop app is installed and running.")
        print("  → Connect GoPro via USB-C cable.")
        print("  → Check the blue dot in system tray GoPro icon.")
=======
        print("[gopro_client] [X] No USB GoPro webcam device found.")
        print("  -> Make sure the GoPro Webcam desktop app is installed and running.")
        print("  -> Connect GoPro via USB-C cable.")
        print("  -> Check the blue dot in system tray GoPro icon.")
>>>>>>> Stashed changes
        return False

    def _open_gopro_wifi(self) -> bool:
        """
<<<<<<< Updated upstream
        Open GoPro via direct WiFi AP connection (laptop WiFi → GoPro WiFi).
=======
        Open GoPro via direct WiFi AP connection (laptop WiFi -> GoPro WiFi).
>>>>>>> Stashed changes
        GoPro is at 10.5.5.9 (or configured --gopro-ip).
        """
        ip = self.gopro_ip
        print(f"[gopro_client] Connecting to GoPro WiFi AP at {ip}...")
        base = f"http://{ip}:8080"

        # Signal GoPro to start preview stream
        try:
            requests.get(f"{base}/gopro/camera/state", timeout=2)
            requests.get(f"{base}/gopro/camera/stream/start", timeout=2)
<<<<<<< Updated upstream
            print(f"[gopro_client] ✓ GoPro stream start signaled via HTTP.")
        except Exception as e:
            print(f"[gopro_client] ✗ GoPro HTTP API unreachable at {ip}: {e}")
            print(f"  → Is your laptop WiFi connected to the GoPro's WiFi network?")
            print(f"  → The GoPro WiFi SSID is usually 'GP-XXXXXXXX'")

        return self._open_udp_stream(ip)
=======
            print(f"[gopro_client] [OK] GoPro stream start signaled via HTTP.")
            return self._open_udp_stream(ip)
        except Exception as e:
            self.status = "GoPro Disconnected (10.5.5.9). Connect to GoPro Wi-Fi or USB."
            print(f"[gopro_client] [X] GoPro HTTP API unreachable at {ip}: {e}")
            print(f"  -> Is your laptop WiFi connected to the GoPro's WiFi network?")
            print(f"  -> The GoPro WiFi SSID is usually 'GP-XXXXXXXX'")
            return False
>>>>>>> Stashed changes

    def _open_gopro_hotspot(self) -> bool:
        """
        Open GoPro that's connected to an external WiFi (phone hotspot).
        Must discover the GoPro's DHCP-assigned IP first.
        """
        print("[gopro_client] Hotspot mode: discovering GoPro on local network...")

        # Step 1: Try ARP table first (fast)
        ip = arp_find_gopro()

        # Step 2: If ARP didn't work, do subnet scan
        if ip is None:
            ip = scan_for_gopro(timeout=1.0)

        if ip is None:
            self.status = "GoPro not found on hotspot network"
<<<<<<< Updated upstream
            print("[gopro_client] ✗ Could not find GoPro on the network.")
            print("  → Make sure GoPro is connected to the same hotspot as this laptop.")
            print("  → Check your phone's hotspot connected devices for the GoPro's IP.")
            print("  → You can manually specify: --gopro-ip <ip_from_hotspot>")
=======
            print("[gopro_client] [X] Could not find GoPro on the network.")
            print("  -> Make sure GoPro is connected to the same hotspot as this laptop.")
            print("  -> Check your phone's hotspot connected devices for the GoPro's IP.")
            print("  -> You can manually specify: --gopro-ip <ip_from_hotspot>")
>>>>>>> Stashed changes
            return False

        self._hotspot_gopro_ip = ip
        base = f"http://{ip}:8080"

        # Signal GoPro to start preview stream
        try:
            requests.get(f"{base}/gopro/camera/state", timeout=2)
<<<<<<< Updated upstream
            print(f"[gopro_client] ✓ GoPro HTTP API responding at {ip}")
            requests.get(f"{base}/gopro/camera/stream/start", timeout=2)
            print(f"[gopro_client] ✓ Stream start signaled.")
        except Exception as e:
            print(f"[gopro_client] ⚠ GoPro HTTP API at {ip} — {e}")
            print(f"  → The GoPro may block API in STA mode on newer firmware.")
            print(f"  → Consider USB webcam mode instead (--source usb)")
=======
            print(f"[gopro_client] [OK] GoPro HTTP API responding at {ip}")
            requests.get(f"{base}/gopro/camera/stream/start", timeout=2)
            print(f"[gopro_client] [OK] Stream start signaled.")
        except Exception as e:
            print(f"[gopro_client] [!] GoPro HTTP API at {ip} - {e}")
            print(f"  -> The GoPro may block API in STA mode on newer firmware.")
            print(f"  -> Consider USB webcam mode instead (--source usb)")
>>>>>>> Stashed changes

        return self._open_udp_stream(ip)

    def _open_udp_stream(self, gopro_ip: str) -> bool:
        """Open the GoPro's UDP preview stream."""
        urls = [
            "udp://0.0.0.0:8554?overrun_nonfatal=1&fifo_size=50000000",
            f"udp://{gopro_ip}:8554?overrun_nonfatal=1&fifo_size=50000000",
            "udp://@:8554?overrun_nonfatal=1",
        ]
        for u in urls:
            try:
                cap = cv2.VideoCapture(u, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                if cap.isOpened():
                    self._cap = cap
                    self.status = f"GoPro Stream Connected ({gopro_ip})"
<<<<<<< Updated upstream
                    print(f"[gopro_client] ✓ Connected to UDP stream: {u}")
=======
                    print(f"[gopro_client] [OK] Connected to UDP stream: {u}")
>>>>>>> Stashed changes
                    return True
            except Exception as e:
                print(f"[gopro_client] Error trying {u}: {e}")

        self.status = f"Waiting for GoPro stream at {gopro_ip}..."
        return False

    def _open_sample_video(self) -> bool:
        """
        Open pre-recorded sample drone footage for demo and testing.
        Automatically loops continuously.
        """
        print(f"[gopro_client] Opening sample footage: {self.sample_path}...")
        if not os.path.exists(self.sample_path):
            self.status = f"Sample clip not found: {os.path.basename(self.sample_path)}"
<<<<<<< Updated upstream
            print(f"[gopro_client] ✗ Sample clip not found at: {self.sample_path}")
=======
            print(f"[gopro_client] [ERROR] Sample clip not found at: {self.sample_path}")
>>>>>>> Stashed changes
            return False

        cap = cv2.VideoCapture(self.sample_path)
        if cap.isOpened():
            self._cap = cap
            fps_val = cap.get(cv2.CAP_PROP_FPS)
            self._sample_fps = fps_val if (fps_val and fps_val > 0) else 25.0
            actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
<<<<<<< Updated upstream
            self.status = f"Sample Footage Active ({actual_w}x{actual_h} @ {int(self._sample_fps)}fps)"
            print(f"[gopro_client] ✓ Sample footage loaded: {actual_w}x{actual_h} ({self._sample_fps} fps). Looping enabled.")
=======
            clip_title = self.active_clip["title"] if self.active_clip else os.path.basename(self.sample_path)
            self.status = f"{clip_title} ({actual_w}x{actual_h} @ {int(self._sample_fps)}fps)"
            print(f"[gopro_client] [OK] Sample footage loaded: {actual_w}x{actual_h} ({self._sample_fps:.1f} fps). Looping enabled.")
>>>>>>> Stashed changes
            return True

        self.status = "Failed to load sample clip"
        return False

    # ── Main open dispatcher ─────────────────────────────────────

    def _open_camera(self) -> bool:
        self._release_cap()

        if self.source == "webcam":
            return self._open_webcam()
        elif self.source == "usb":
            return self._open_usb_gopro()
        elif self.source == "gopro":
            return self._open_gopro_wifi()
        elif self.source == "hotspot":
            return self._open_gopro_hotspot()
        elif self.source == "sample":
            return self._open_sample_video()
<<<<<<< Updated upstream
=======
        elif self.source == "scenario":
            return self._scenario_frame is not None
>>>>>>> Stashed changes

        return False

    # ── Worker loops ─────────────────────────────────────────────

    def _capture_loop(self):
        while self.running:
<<<<<<< Updated upstream
=======
            # 1. Handle auto-cycling through scenarios and clips if enabled
            if self.auto_cycle and (len(self.scenarios) > 0 or len(self.clips) > 0):
                now = time.time()
                if self.last_cycle_time == 0.0 or (now - self.last_cycle_time) >= self.cycle_interval:
                    self.last_cycle_time = now
                    total_items = len(self.scenarios) + len(self.clips)
                    if self.cycle_idx < len(self.scenarios):
                        sc = self.scenarios[self.cycle_idx]
                        self.set_scenario(sc["id"])
                    else:
                        clip_idx = self.cycle_idx - len(self.scenarios)
                        if clip_idx < len(self.clips):
                            cl = self.clips[clip_idx]
                            self.set_clip(cl["id"])
                    self.cycle_idx = (self.cycle_idx + 1) % max(1, total_items)

            # 2. Handle static scenario frame streaming
            if self.source == "scenario":
                if self._scenario_frame is not None:
                    with self._lock:
                        self._ret = True
                        self._frame = self._scenario_frame.copy()
                    time.sleep(0.04)  # ~25 fps live streaming
                else:
                    time.sleep(0.1)
                continue

>>>>>>> Stashed changes
            if self._cap is None or not self._cap.isOpened():
                success = self._open_camera()
                if not success:
                    with self._lock:
                        self._frame = create_placeholder_frame(self.status)
                        self._ret = True
                    # Longer retry for discovery-heavy modes
                    sleep = 5.0 if self.source == "hotspot" else 2.0
                    time.sleep(sleep)
                    continue

            try:
                ret, frame = self._cap.read()
                if ret and frame is not None:
                    with self._lock:
                        self._ret = True
                        self._frame = frame

                    if self.source == "sample":
                        # Pace playback according to video FPS (~25 fps -> 40ms per frame)
                        delay = 1.0 / max(1.0, self._sample_fps)
                        time.sleep(delay)
                else:
                    if self.source == "sample" and self._cap is not None:
                        # Seamless loop: rewind back to frame 0
                        self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        time.sleep(0.02)
                    else:
                        time.sleep(0.04)
            except Exception as e:
                print(f"[gopro_client] Capture error: {e}")
                self._release_cap()
                time.sleep(1.0)

    def _keepalive_loop(self):
        while self.running:
            if self.source in ("gopro", "hotspot"):
                ip = self.active_gopro_ip
                try:
                    requests.get(
                        f"http://{ip}:8080/gopro/camera/stream/keep_alive",
                        timeout=1.0,
                    )
                except Exception:
                    pass
            time.sleep(2.5)


# ── FastAPI App ──────────────────────────────────────────────────────

camera = CameraStreamer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    camera.start()
    yield
    camera.stop()


app = FastAPI(title="GoPro Handler Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "source": camera.source,
        "detail": camera.status,
        "gopro_ip": camera.active_gopro_ip,
<<<<<<< Updated upstream
=======
        "scenario": camera.active_scenario,
        "active_clip": camera.active_clip,
        "clips_count": len(camera.clips),
        "auto_cycle": camera.auto_cycle,
    }


@app.get("/clips")
def get_clips():
    """List all available demo video clips."""
    return {
        "status": "ok",
        "clips": camera.clips,
        "active_clip": camera.active_clip,
    }


@app.post("/clip")
def select_clip(id: str):
    """Switch camera source to a specific video clip."""
    ok, res = camera.set_clip(id)
    if not ok:
        raise HTTPException(400, detail=res)
    return {"status": "ok", "clip": res}



@app.get("/scenarios")
def get_scenarios():
    """List all curated VisDrone crowd scenarios for demo evaluation."""
    return {
        "status": "ok",
        "scenarios": camera.scenarios,
        "active_scenario": camera.active_scenario,
        "auto_cycle": camera.auto_cycle,
        "cycle_interval": camera.cycle_interval,
    }


@app.post("/scenario")
def select_scenario(id: str):
    """Switch camera source to a specific VisDrone crowd scenario."""
    ok, res = camera.set_scenario(id)
    if not ok:
        raise HTTPException(400, detail=res)
    return {"status": "ok", "scenario": res}


@app.post("/scenario/cycle")
def toggle_scenario_cycle(enabled: bool = None, interval: float = None):
    """Toggle or configure automatic cycling through all demo scenarios."""
    state = camera.toggle_auto_cycle(enabled, interval)
    return {
        "status": "ok",
        "auto_cycle": state,
        "cycle_interval": camera.cycle_interval,
>>>>>>> Stashed changes
    }


@app.post("/source")
<<<<<<< Updated upstream
def switch_source(source: str):
=======
async def switch_source(req: Request, source: str = None):
    if not source:
        try:
            body = await req.json()
            source = body.get("source")
        except Exception:
            pass
    if not source:
        raise HTTPException(400, detail="Missing 'source' in query parameter or JSON body")
>>>>>>> Stashed changes
    ok, msg = camera.set_source(source)
    if not ok:
        raise HTTPException(400, detail=msg)
    return {"status": "ok", "source": msg}


@app.get("/capture")
def capture_frame():
    """Returns single JPEG frame for AI analysis."""
    ret, frame = camera.read_frame()
    if not ret or frame is None:
        raise HTTPException(503, detail="Camera frame not available")

    success, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not success:
        raise HTTPException(500, detail="Failed to encode frame")

    return Response(content=encoded.tobytes(), media_type="image/jpeg")


@app.get("/preview")
def preview_feed():
    """Streams MJPEG preview for the dashboard/browser."""
    async def frame_generator():
        try:
            while True:
                ret, frame = camera.read_frame()
                if ret and frame is not None:
                    _, buf = cv2.imencode(
                        ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60]
                    )
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + buf.tobytes()
                        + b"\r\n"
                    )
                await asyncio.sleep(0.04)  # ~25 fps
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# ── CLI Entry Point ──────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GoPro Handler Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Connection modes:
  gopro     Direct WiFi AP (laptop WiFi → GoPro WiFi, IP 10.5.5.9)
            Best latency. Use USB tethering for internet.
  usb       USB-C cable + GoPro Webcam Utility app.
            Best latency. WiFi free for internet.
  hotspot   GoPro on phone hotspot. Auto-discovers GoPro IP.
            Convenient but higher latency.
  webcam    Laptop built-in webcam (testing fallback).

Examples:
  python gopro_client.py --source gopro
  python gopro_client.py --source usb
  python gopro_client.py --source usb --usb-index 1
  python gopro_client.py --source hotspot
  python gopro_client.py --source webcam
        """,
    )
    parser.add_argument("--port", type=int, default=8081, help="Server port (default: 8081)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Bind address")
    parser.add_argument("--gopro-ip", type=str, default=GOPRO_IP, help="GoPro IP for WiFi AP mode (default: 10.5.5.9)")
    parser.add_argument(
        "--source", type=str, default="gopro",
        choices=VALID_SOURCES,
        help="Camera source (default: gopro)",
    )
    parser.add_argument(
        "--usb-index", type=int, default=None,
        help="USB webcam device index (default: auto-detect)",
    )
    parser.add_argument(
        "--sample-path", type=str, default=DEFAULT_SAMPLE_PATH,
        help="Path to sample video file for demo mode (default: test/clip.mp4)",
    )
<<<<<<< Updated upstream
=======
    parser.add_argument(
        "--scenario", type=str, default=None,
        help="Initial scenario ID (e.g., low_park, moderate_campus, high_plaza, critical_market)",
    )
    parser.add_argument(
        "--auto-cycle", action="store_true",
        help="Automatically cycle through all dataset scenarios during demo",
    )
    parser.add_argument(
        "--cycle-interval", type=float, default=8.0,
        help="Interval in seconds between scenario transitions (default: 8.0)",
    )
>>>>>>> Stashed changes
    args = parser.parse_args()

    camera.gopro_ip = args.gopro_ip
    camera.source = args.source
    camera.usb_index = args.usb_index
    camera.sample_path = args.sample_path

<<<<<<< Updated upstream
    print("=" * 60)
    print("  GoPro Handler Server")
    print("=" * 60)
    print(f"  Source:   {args.source}")
    print(f"  Host:     {args.host}:{args.port}")
    if args.source == "gopro":
        print(f"  GoPro IP: {args.gopro_ip}")
    elif args.source == "usb":
        print(f"  USB idx:  {args.usb_index or 'auto-detect'}")
    elif args.source == "hotspot":
        print(f"  Network:  auto-discover GoPro on local subnet")
    elif args.source == "sample":
        print(f"  Sample:   {args.sample_path}")
=======
    if args.scenario:
        camera.set_scenario(args.scenario)
    elif args.auto_cycle:
        camera.toggle_auto_cycle(True, interval=args.cycle_interval)

    print("=" * 60)
    print("  GoPro Handler Server")
    print("=" * 60)
    print(f"  Source:   {camera.source}")
    print(f"  Host:     {args.host}:{args.port}")
    if camera.source == "gopro":
        print(f"  GoPro IP: {args.gopro_ip}")
    elif camera.source == "usb":
        print(f"  USB idx:  {args.usb_index or 'auto-detect'}")
    elif camera.source == "hotspot":
        print(f"  Network:  auto-discover GoPro on local subnet")
    elif camera.source == "sample":
        print(f"  Sample:   {args.sample_path}")
    elif camera.source == "scenario":
        print(f"  Scenario: {camera.active_scenario['title'] if camera.active_scenario else 'Active'}")
    if camera.auto_cycle:
        print(f"  AutoCycle: ENABLED ({camera.cycle_interval}s interval)")
>>>>>>> Stashed changes
    print("=" * 60)
    uvicorn.run(app, host=args.host, port=args.port)
