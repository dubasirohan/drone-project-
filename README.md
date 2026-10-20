# AI-Powered Drone System for Real-Time Crowd Management and Monitoring

**BCSE497J: Project I** | School of Computer Science and Engineering, VIT Chennai
**Guide:** Prof. Valarmathi Sudhakar

**Team**
- Rohan Dubasi (23BRS1119)
- Tejas Ramesh Bodetti (23BRS1180)

## Overview

Large gatherings risk stampedes and dangerous congestion, and fixed CCTV cannot cover blind spots or respond to what it sees. This project combines a manually piloted quadcopter with a ground-station AI pipeline and an onboard acoustic unit, so crowd density can be detected in real time and answered with automated sirens or spoken announcements.

The drone is **operator-piloted** (FlySky radio, Pixhawk 2.4.8 running ArduPilot). It is not autonomous. The ground station analyses the video and shows results to a human operator, who decides how to respond.

## How It Works

```text
Drone (S500 + GoPro Hero 13 + ESP32 speaker)
        │  Wi-Fi (GoPro access point 10.5.5.9, UDP video on port 8554)
        ▼
Ground station laptop
  gopro_client.py     ->  video handler (port 8081)
  analysis_server.py  ->  YOLOv8 detection -> 3x4 zone counting -> density alerts
                          FastAPI + WebSocket dashboard (port 8082)
  esp32_manager.py    ->  audio generation + TCP bridge to ESP32 (port 8002)
        │                                   │
        ▼                                   ▼
Web dashboard                     ESP32 speaker (siren / chime / voice)
```

The ground station uses two Wi-Fi adapters: one connects directly to the GoPro's access point for low-latency video, and the other carries dashboard, telemetry and ESP32 traffic. Measured mean video latency is about 102 ms, compared with about 345 ms over a shared hotspot and about 580 ms with RTSP over TCP.

## Repository Structure

```text
src/
  gopro_client.py        Video source handler (GoPro UDP, USB, hotspot, webcam, demo clip)
  analysis_server.py     YOLOv8 inference, zone counting, alerts, REST + WebSocket API
  esp32_manager.py       Siren/chime/alarm synthesis, gTTS voice, TCP audio streaming to ESP32
  density/zone_counter.py  Standalone offline 3x4 zone counting script (writes video + CSV)
esp32/
  crowd_speaker.ino      ESP32 firmware (DAC audio out, emergency button, TCP client)
dashboard/
  index.html             Mission control web dashboard
test/
  clip.mp4               Sample aerial footage for demo mode
runs/detect/track/       Offline ByteTrack tracking output
start.bat                Launch for live GoPro mode (Windows)
start_demo.bat           One-click demo launcher using the test clip (Windows)
```

## Features

**Detection and density**
- YOLOv8 person detection (class 0, confidence threshold 0.25)
- The frame is split into a 3x4 grid (12 zones); each person is assigned by bounding-box center
- Per-zone density bands:

| Band | People in zone | Action |
|------|----------------|--------|
| Low | 0 to 5 | Normal monitoring |
| Medium | 6 to 15 | Logged, operator notice |
| High | 16 to 25 | Warning alert |
| Critical | over 25 | Critical alert |

- An overall scene density (low / moderate / elevated / critical) is computed from the average people per zone

**Acoustic intervention**
- Presets: Emergency Siren, Attention Chime, Evacuation Alarm, Warning Beeps
- Voice presets: Disperse Notice, Crowd Density Warning, Emergency Evacuate
- Custom text-to-speech messages in multiple languages (gTTS)
- ESP32 plays audio through its DAC on **GPIO 25**; a physical emergency button is on **GPIO 14** (active LOW)
- Audio format: 8 kHz, unsigned 8-bit PCM sent over TCP with a 6-byte header (magic bytes `A5 5A` + 4-byte little-endian length). The ESP32 replies `RECEIVING` and `DONE`, announces itself with `ESP32_READY`, and sends `BTN` on button press

**Dashboard**
- Live video with zone overlay, FPS, and source switching (GoPro Live, Demo Footage, Laptop Webcam)
- Scene density status, total and peak people count, 3x4 heatmap, alert feed, history chart
- Drone status panel and ESP32 speaker controls
- Demo mode loops the test clip so the system can be shown without flying

## Setup

**Requirements:** Python 3.10+, FFmpeg on PATH (used for voice audio resampling), a CUDA GPU is recommended but not required.

```bash
pip install -r requirements.txt
```

**ESP32:** open `esp32/crowd_speaker.ino`, set `WIFI_SSID`, `WIFI_PASSWORD` and `LAPTOP_IP` for your network, then flash it. Do not commit real credentials.

## Running

**Demo mode (no drone needed):**
```bat
start_demo.bat
```

**Live mode (GoPro connected on its own Wi-Fi adapter):**
```bat
start.bat
```

Or start the services manually:
```bash
python src/gopro_client.py --source sample --port 8081
python src/analysis_server.py --port 8082 --esp32-port 8002
```
Then open http://localhost:8082. Video sources for `gopro_client.py`: `gopro`, `usb`, `hotspot`, `webcam`, `sample`.

## API Endpoints (port 8082)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Dashboard |
| GET | `/health` | Service health |
| GET | `/stats` | Latest counts, zones, alerts |
| GET | `/drone/status` | Drone status |
| GET | `/network/info` | Local network addresses |
| GET | `/esp32/status` | ESP32 connection state |
| POST | `/esp32/play` | Play a preset or custom TTS message |
| POST | `/esp32/stop` | Stop audio |
| WS | `/ws` | Live telemetry and analysis stream |

## Results (from the project report)

| Metric | Target | Measured |
|--------|--------|----------|
| Thrust-to-weight ratio | above 2.0 | 2.286 (3,840 gf peak, 1,680 gf AUW) |
| Hover endurance | above 15 min | 17.8 min (18.05 min predicted) |
| Video latency | below 150 ms | 102 ms mean |
| Closed-loop response | below 150 ms | 145.4 ms |
| Tracking (ByteTrack tuning) | stable IDs | cumulative IDs 284 to 54, MOTA 58.2% to 88.6% |
| YOLOv8n vs YOLOv8x | | 70.4 vs 11.6 FPS; recall 92.4% vs 96.8% |

Vision results come from a single 341-frame clip with 42 to 45 people, so dense-crowd and varied-lighting performance is not yet evaluated.

## Implementation Status

| Component | Status |
|-----------|--------|
| Drone hardware assembly and flight testing | Done |
| YOLOv8 person detection | Done |
| 3x4 zone counting and density classification | Done |
| Alert generation | Done |
| ESP32 audio unit and TCP bridge | Done |
| Web dashboard | Done |
| Demo mode with looping test clip | Done |
| ByteTrack tracking | Validated offline; not yet in the live server loop |
| GPS localization (pinhole projection + ArduPilot telemetry) | Model derived; alert GPS fields not yet populated |
| Live telemetry integration | In progress |
| Crowd flow analysis | Planned |

## Future Work

- Integrate ByteTrack into the live analysis loop
- Populate alert GPS coordinates from flight telemetry
- MAVLink GUIDED-mode repositioning toward critical zones
- On-drone edge NPU inference (e.g. Hailo-8)
- 2-axis brushless gimbal for stable nadir view
- Multi-UAV cooperative swarm using ROS 2
