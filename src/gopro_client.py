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
import os
import socket
import struct
import subprocess
import threading
import time
from contextlib import asynccontextmanager

import cv2
import numpy as np
import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# ── Low-latency FFMPEG tuning ────────────────────────────────────────
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "fflags;nobuffer|flags;low_delay|framedrop;1"
)

GOPRO_IP = os.getenv("GOPRO_IP", "10.5.5.9")
VALID_SOURCES = ("gopro", "usb", "hotspot", "webcam")


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
                print(f"[gopro_client] ✓ Found GoPro at {ip}")
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
                            print(f"[gopro_client] ✓ Found GoPro at {ip_candidate} (via ARP)")
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
                 usb_index: int = None):
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

        # Hotspot mode: discovered IP
        self._hotspot_gopro_ip: str | None = None

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
        source = source.lower()
        if source not in VALID_SOURCES:
            return False, f"Source must be one of: {', '.join(VALID_SOURCES)}"
        with self._lock:
            self.source = source
            self._release_cap()
            self._hotspot_gopro_ip = None
            self.status = f"Switching to {source}..."
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
            print("[gopro_client] ✓ Webcam opened.")
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
                    print(f"[gopro_client] ✓ USB webcam opened: device {idx} at {actual_w}x{actual_h}")
                    return True
                cap.release()

        self.status = "USB GoPro not found — is GoPro Webcam Utility running?"
        print("[gopro_client] ✗ No USB GoPro webcam device found.")
        print("  → Make sure the GoPro Webcam desktop app is installed and running.")
        print("  → Connect GoPro via USB-C cable.")
        print("  → Check the blue dot in system tray GoPro icon.")
        return False

    def _open_gopro_wifi(self) -> bool:
        """
        Open GoPro via direct WiFi AP connection (laptop WiFi → GoPro WiFi).
        GoPro is at 10.5.5.9 (or configured --gopro-ip).
        """
        ip = self.gopro_ip
        print(f"[gopro_client] Connecting to GoPro WiFi AP at {ip}...")
        base = f"http://{ip}:8080"

        # Signal GoPro to start preview stream
        try:
            requests.get(f"{base}/gopro/camera/state", timeout=2)
            requests.get(f"{base}/gopro/camera/stream/start", timeout=2)
            print(f"[gopro_client] ✓ GoPro stream start signaled via HTTP.")
        except Exception as e:
            print(f"[gopro_client] ✗ GoPro HTTP API unreachable at {ip}: {e}")
            print(f"  → Is your laptop WiFi connected to the GoPro's WiFi network?")
            print(f"  → The GoPro WiFi SSID is usually 'GP-XXXXXXXX'")

        return self._open_udp_stream(ip)

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
            print("[gopro_client] ✗ Could not find GoPro on the network.")
            print("  → Make sure GoPro is connected to the same hotspot as this laptop.")
            print("  → Check your phone's hotspot connected devices for the GoPro's IP.")
            print("  → You can manually specify: --gopro-ip <ip_from_hotspot>")
            return False

        self._hotspot_gopro_ip = ip
        base = f"http://{ip}:8080"

        # Signal GoPro to start preview stream
        try:
            requests.get(f"{base}/gopro/camera/state", timeout=2)
            print(f"[gopro_client] ✓ GoPro HTTP API responding at {ip}")
            requests.get(f"{base}/gopro/camera/stream/start", timeout=2)
            print(f"[gopro_client] ✓ Stream start signaled.")
        except Exception as e:
            print(f"[gopro_client] ⚠ GoPro HTTP API at {ip} — {e}")
            print(f"  → The GoPro may block API in STA mode on newer firmware.")
            print(f"  → Consider USB webcam mode instead (--source usb)")

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
                    print(f"[gopro_client] ✓ Connected to UDP stream: {u}")
                    return True
            except Exception as e:
                print(f"[gopro_client] Error trying {u}: {e}")

        self.status = f"Waiting for GoPro stream at {gopro_ip}..."
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

        return False

    # ── Worker loops ─────────────────────────────────────────────

    def _capture_loop(self):
        while self.running:
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
    }


@app.post("/source")
def switch_source(source: str):
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
    args = parser.parse_args()

    camera.gopro_ip = args.gopro_ip
    camera.source = args.source
    camera.usb_index = args.usb_index

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
    print("=" * 60)
    uvicorn.run(app, host=args.host, port=args.port)
