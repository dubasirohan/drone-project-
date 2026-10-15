"""
report_sections/ch4_ground_assisted_comms.py — Chapter 4: Ground-Assisted
Architecture & Wireless Communication Infrastructure.
Covers Pixhawk avionics, fail-safes, dual-adapter networking topology,
GoPro low-latency UDP streaming, ESP32 TCP binary audio bridge, and WebSocket telemetry.
"""

import docx
from report_sections.doc_helpers import (
    add_chapter_heading,
    add_section_heading,
    add_subsection_heading,
    add_p,
    add_figure_placeholder,
    add_table_data,
    add_code_snippet
)


def generate_chapter_4(doc: docx.Document):
    """Generate Chapter 4: Architecture & Communication."""
    add_chapter_heading(doc, 4, "Ground-Assisted Architecture & Wireless Communication Infrastructure")

    # 4.1 DISTRIBUTED ARCHITECTURE
    add_section_heading(doc, "4.1", "Distributed Ground-Assisted Architectural Topology")
    add_p(doc,
          "As established in Chapter 3, rotary-wing flight endurance is severely compromised by every additional gram of onboard payload mass. "
          "Mounting an edge computing neural network accelerator (such as an NVIDIA Jetson AGX or Xavier) directly onto the aircraft chassis adds "
          "over 200–260 grams of dead weight and draws 10–15 Watts of continuous power, stripping over 5 to 7 minutes from the vehicle's flight window. "
          "To circumvent this fundamental physical limitation, this system establishes a Distributed Ground-Assisted Robotic Architecture.")

    add_p(doc,
          "The system divides responsibilities between two cooperating functional tiers across an air-to-ground wireless boundary:\n"
          "1. Aerial Airborne Subsystem: Restricted exclusively to flight-critical tasks: motor attitude stabilization, sensor fusion, "
          "inertial navigation, fail-safe execution, raw visual frame acquisition (GoPro Hero 13), and acoustic command delivery (ESP32 horn speaker). "
          "The drone operates as a lightweight, agile aerial sensing and actuation node.\n"
          "2. Ground Station Subsystem: Comprising a high-performance laptop workstation equipped with a discrete NVIDIA RTX 3070 Ti GPU (8GB VRAM). "
          "The ground station executes all computationally intensive operations: low-latency UDP video frame ingestion, YOLOv8 deep learning person "
          "detection, ByteTrack multi-object tracking, 3×4 spatial density estimation, pinhole camera GPS localization, rule-based alert evaluation, "
          "and WebSocket-based mission control visualization.")

    add_figure_placeholder(doc, "4.1",
                           "Distributed Ground-Assisted Robotic System Architecture and Data Flow",
                           "Block diagram mapping data flows between the Airborne Subsystem (GoPro 13, Pixhawk, ESP32 speaker) and Ground Station "
                           "(gopro_client.py, analysis_server.py, YOLOv8, ByteTrack, Dashboard). Highlights the air-to-ground wireless link separation "
                           "and bidirectional acoustic command feedback loop.")

    # 4.2 ONBOARD FLIGHT CONTROL ARCHITECTURE
    add_section_heading(doc, "4.2", "Onboard Flight Control Architecture (Pixhawk 2.4.8 & ArduPilot)")
    add_p(doc,
          "The primary flight control avionics system is the Pixhawk 2.4.8 open-hardware autopilot, running the ArduCopter firmware stack "
          "(version 4.3+). Built around an ARM Cortex-M4 32-bit core (STM32F427 @ 168 MHz) with an independent fail-safe co-processor (STM32F100 @ 24 MHz), "
          "the Pixhawk executes real-time sensor fusion and motor attitude control at 400 Hz.")

    sensor_headers = ["Sensor Subsystem", "Integrated Circuit (IC)", "Measurement Parameters", "Operating Bus & Update Rate"]
    sensor_rows = [
        ["Primary 6-DOF IMU", "InvenSense MPU-6000", "3-Axis Angular Gyro (±2000°/s) + 3-Axis Accel (±16g)", "SPI Bus @ 1.0 kHz Internal Sampling"],
        ["Secondary 6-DOF IMU", "STMicroelectronics LSM303D + L3GD20H", "Auxiliary 3-Axis Accel + 3-Axis Gyroscope (Redundancy)", "I2C / SPI Bus @ 400 Hz Sampling"],
        ["Barometric Altimeter", "MEAS MS5611-01BA03", "Atmospheric Static Pressure (10–1200 mbar, 10 cm resolution)", "I2C Bus @ 50 Hz Update Rate"],
        ["External Compass / GNSS", "Ublox Neo-M8N + HMC5983", "72-Channel Concurrent GPS/GLONASS (2.5m CEP) + 3-Axis Compass", "UART @ 115200 baud (5 Hz GPS) + I2C (Compass)"],
        ["Power Sense Module", "Allegro Hall-Effect Shunt BEC", "Real-Time Battery Bus Voltage (0–18V) + Pack Current (0–90A)", "Analog ADC Pins (Battery Monitor)"]
    ]
    add_table_data(doc, "4.1", "Avionics Sensor Suite Specifications for Pixhawk 2.4.8",
                   sensor_headers, sensor_rows, col_widths=[1.5, 1.8, 2.0, 1.2])

    add_p(doc,
          "Autonomous Fail-safe Architecture:\n"
          "To guarantee strict operational safety during crowd loitering missions, four automated hardware and software fail-safes are configured "
          "within ArduPilot:\n"
          "1. Battery Voltage / Capacity Failsafe: Monitored via the analog power module. If total battery voltage sags below $14.0\\text{ V}$ "
          "($3.5\\text{ V/cell}$) or consumed capacity exceeds $4,160\\text{ mAh}$ (80% DOD), the flight controller automatically aborts current "
          "operations and initiates an autonomous Return-to-Launch (RTL) flight path to the home takeoff coordinates.\n"
          "2. Radio Control (RC) Link Loss Failsafe: Monitored via the FlySky FS-iA6B i-Bus serial link. If the 2.4 GHz control signal is lost for "
          "more than 1.5 seconds, the drone immediately pauses, ascends to a safe cruising altitude of 25 meters, and executes automated RTL.\n"
          "3. Cylindrical Software Geofencing: A hardware-enforced virtual boundary is established in non-volatile EEPROM. The maximum operating radius "
          "is hard-limited to 150 meters from the home point, with an altitude floor of 10 meters and ceiling of 45 meters. Any boundary breach triggers "
          "instant hover braking and autonomous RTL.\n"
          "4. Manual Hardware RC Override: Regardless of autonomous flight commands issued by the ground station, the human pilot retains instant, "
          "direct hardware override authority on the FlySky FS-i6 transmitter via the primary flight mode toggle switch (Switch C).")

    add_figure_placeholder(doc, "4.2",
                           "Pixhawk 2.4.8 Internal Sensor Bus Architecture and Fail-safe Redundancy Loops",
                           "Schematic showing the dual-bus architecture of the Pixhawk 2.4.8 autopilot. Illustrates the SPI bus connecting the MPU-6000 "
                           "IMU to the primary STM32F427 CPU, the I2C bus connecting the external compass and barometer, the fail-safe co-processor "
                           "monitoring RC inputs, and the state-machine logic governing automated Return-to-Launch triggers.")

    # 4.3 DUAL-ADAPTER WIRELESS NETWORKING
    add_section_heading(doc, "4.3", "Dual-Adapter High-Performance Wireless Networking Architecture")
    add_p(doc,
          "A major technical hurdle encountered during initial prototyping was the 'Single-Adapter Wireless Bottleneck.' When a conventional "
          "laptop connects its single internal Wi-Fi adapter to an external mobile hotspot (to communicate with the local network, ESP32, and "
          "internet), it cannot simultaneously connect to the GoPro's dedicated Access Point Wi-Fi network (which operates on subnet `10.5.5.0/24`).\n"
          "Conversely, if the laptop connects directly to the GoPro's Access Point, it gains access to the low-latency camera stream at `10.5.5.9`, "
          "but completely severs its connection to the ESP32 speaker, client dashboard devices, and internet-based Text-to-Speech (TTS) voice engines.")

    add_p(doc,
          "Attempting to force the GoPro into Station Mode (STA mode) connected to a common mobile hotspot proved disastrous: GoPro firmware "
          "actively restricts its high-throughput UDP streaming ports across external subnets, introduces unpredictable DHCP lease assignments, "
          "and subjects the video stream to severe RF packet contention with ground station traffic, causing stream latency to surge from 100 ms to over 1,800 ms.")

    add_p(doc,
          "To decisively resolve this architectural deadlock, a Dual-Adapter High-Performance Wireless Topology was engineered on the ground station. "
          "The laptop utilizes two physically independent network interface cards (NICs), as delineated in Table 4.2:")

    net_headers = ["Network Interface", "Hardware Adapter", "Assigned Subnet", "Connected Remote Node", "Functional Traffic Role"]
    net_rows = [
        ["Adapter 1 (Video Link)", "High-Gain USB Wi-Fi Adapter (Realtek RTL8812AU 802.11ac)", "10.5.5.x (DHCP Client from GoPro)", "GoPro Hero 13 AP (10.5.5.9:8080)", "DEDICATED VIDEO INGEST: Ultra-low latency raw UDP :8554 stream"],
        ["Adapter 2 (Telemetry Link)", "Internal Laptop Wi-Fi 6 NIC (Intel AX201) / Mobile Tether", "172.20.10.x (DHCP from 'TPhone')", "ESP32 Speaker (Client) & Dashboard Clients", "COMMAND & TELEMETRY: Port 8002 TCP Audio Server, Port 8082 Web Dashboard, Internet TTS"]
    ]
    add_table_data(doc, "4.2", "Dual-Adapter Network Interface Architecture & IP Subnet Allocation",
                   net_headers, net_rows, col_widths=[1.5, 1.6, 1.4, 1.5, 1.5])

    add_figure_placeholder(doc, "4.3",
                           "Dual-Adapter High-Performance Wireless Network Topology on Ground Station",
                           "Network architectural diagram showing the complete air-to-ground dual link. Adapter 1 establishes a point-to-point "
                           "2.4 GHz link to the GoPro AP (`10.5.5.9`) on port 8554 UDP, while Adapter 2 connects to the mobile hotspot (`TPhone`), "
                           "hosting the ESP32 TCP server on port 8002 and serving the web dashboard on port 8082 to operator tablets and workstations.")

    add_p(doc,
          "By binding the operating system routing table such that traffic destined for `10.5.5.0/24` exclusively traverses Adapter 1, while default "
          "gateway traffic (`0.0.0.0/0`) and local subnet traffic (`172.20.10.0/24`) route through Adapter 2, zero cross-traffic packet contention "
          "occurs. The ground station ingests unthrottled video frames while simultaneously streaming audio to the ESP32 and maintaining live "
          "cloud TTS synthesis.")

    # 4.4 LOW-LATENCY VIDEO PIPELINE
    add_section_heading(doc, "4.4", "Low-Latency Video Pipeline Implementation (`gopro_client.py`)")
    add_p(doc,
          "The ingestion, decoding, and rebroadcasting of the live aerial video feed is executed by a dedicated, asynchronous Python service: "
          "`gopro_client.py` (running on Ground Station Port 8081).")

    add_p(doc,
          "Protocol Comparison: To achieve minimal streaming latency, various transport protocols were evaluated on the ground station:")

    proto_headers = ["Transport Protocol", "Transport Layer", "Observed Latency", "CPU Decoding Overhead", "Suitability for AI Detection"]
    proto_rows = [
        ["HTTP Live Streaming (HLS)", "TCP / Chunked", "3,200–5,500 ms", "Low (~4% CPU)", "Unusable (Severe lag prevents real-time alerting)"],
        ["RTMP (Real-Time Messaging)", "TCP / Streamed", "850–1,400 ms", "Moderate (~8% CPU)", "Poor (TCP retransmissions stall inference)"],
        ["RTSP over TCP", "TCP / RTP", "420–750 ms", "Moderate (~9% CPU)", "Sub-optimal (Buffer spikes during frame drops)"],
        ["Direct UDP Stream (FFmpeg tuned)", "UDP / Raw MPEG-TS", "95–130 ms", "Low (~5% CPU)", "OPTIMAL: Sub-100ms real-time computer vision"]
    ]
    add_table_data(doc, "4.3", "Video Streaming Transport Protocol Comparison (UDP vs. RTSP vs. WebRTC vs. RTMP)",
                   proto_headers, proto_rows, col_widths=[1.5, 1.2, 1.2, 1.3, 1.3])

    add_p(doc,
          "Low-Latency Tuning Implementation: To force the underlying FFmpeg demuxer to completely bypass internal frame queues, the following "
          "environment variable is programmatically injected prior to initializing OpenCV:")
    add_code_snippet(doc,
                     "os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = (\n"
                     "    'fflags;nobuffer|flags;low_delay|framedrop;1'\n"
                     ")",
                     caption="FFmpeg Low-Latency Environment Configuration")

    add_p(doc,
          "Furthermore, the camera streamer initiates capture using a multi-threaded architecture:\n"
          "1. Capture Thread (`_capture_loop`): Executes continuously in a daemon thread, grabbing frames from the UDP socket at 25–30 FPS with "
          "buffer size constrained to $1$ (`cv2.CAP_PROP_BUFFERSIZE = 1`). Whenever a new frame arrives, it overwrites the thread-safe shared "
          "memory buffer protected by a threading `Lock()`. If the AI engine is momentarily busy, stale frames are discarded, guaranteeing that "
          "the detection pipeline always processes the freshest available frame.\n"
          "2. Keep-Alive Ping Thread (`_keepalive_loop`): The GoPro Hero 13 automatically terminates its UDP stream if it does not receive an active "
          "keep-alive heartbeat within 3.0 seconds. A background worker issues an HTTP GET request to `http://10.5.5.9:8080/gopro/camera/stream/keep_alive` "
          "every 2.5 seconds, maintaining continuous stream survival.\n"
          "3. Dual Endpoints: Exposes `/capture` returning single uncompressed JPEG frames for AI inference, and `/preview` returning a multi-client "
          "multipart MJPEG stream for real-time browser dashboard display.")

    add_figure_placeholder(doc, "4.4",
                           "Low-Latency UDP Video Ingestion and MJPEG Streaming Pipeline Architecture",
                           "Architectural diagram of gopro_client.py. Depicts the GoPro UDP stream entering the low-latency FFmpeg demuxer, "
                           "the daemon capture thread buffering the latest frame in thread-safe memory, the keep-alive ping worker maintaining stream state, "
                           "and the FastAPI endpoints serving the AI detection engine (/capture) and web dashboard (/preview).")

    # 4.5 ESP32 WIRELESS AUDIO STREAMING PROTOCOL
    add_section_heading(doc, "4.5", "ESP32 Wireless Audio Streaming & Button Interrupt Protocol (`esp32_manager.py`)")
    add_p(doc,
          "A major contribution of this thesis is the implementation of an active crowd intervention bridge: `esp32_manager.py` (operating on "
          "Ground Station TCP Port 8002). The system streams real-time synthetic siren tones, attention bells, and text-to-speech voice announcements "
          "directly into the drone's airborne ESP32 speaker unit.")

    add_p(doc,
          "Binary Packet Framing Specification:\n"
          "Because the ESP32 microcontroller features limited RAM and no high-level media decoding hardware, audio must be delivered in uncompressed, "
          "raw 8-bit unsigned Pulse-Code Modulation (PCM) sampled at exactly 8,000 Hz. The binary packet structure is defined in Table 4.4:")

    audio_frame_headers = ["Byte Offset", "Field Name", "Data Type", "Value / Description", "Functional Purpose"]
    audio_frame_rows = [
        ["0", "Magic Byte 1", "uint8_t", "0xA5 (165 decimal)", "Frame synchronization preamble"],
        ["1", "Magic Byte 2", "uint8_t", "0x5A (90 decimal)", "Frame synchronization preamble"],
        ["2 – 5", "Payload Length", "uint32_t (Little-Endian)", "4-byte integer (e.g., 24,000 for 3s audio)", "Specifies exact count of PCM sample bytes following"],
        ["6 – (N+5)", "Raw PCM Audio Samples", "uint8_t array", "Unsigned 8-bit samples (0–255, center 128)", "Streamed to ESP32 DAC Channel 1 (GPIO 25)"]
    ]
    add_table_data(doc, "4.4", "ESP32 Binary Audio Streaming Protocol Frame Definition",
                   audio_frame_headers, audio_frame_rows, col_widths=[1.0, 1.3, 1.4, 1.5, 1.3])

    add_figure_placeholder(doc, "4.5",
                           "ESP32 Wireless Audio Streaming & Button Interrupt Protocol Timing Diagram",
                           "Timing sequence diagram showing the TCP handshake: ESP32 connects to ground station port 8002 and sends 'ESP32_READY\\n'. "
                           "Ground station sends 0xA5 0x5A header with audio length; ESP32 responds 'RECEIVING\\n'; ground station streams paced 128-byte "
                           "chunks; ESP32 writes to DAC GPIO 25 at 8kHz, finishes, centers DAC to 128, and sends 'DONE\\n'. Also shows asynchronous 'BTN\\n' interrupt.")

    add_p(doc,
          "Paced Audio Transmission Algorithm: If the ground station transmits the entire audio buffer across TCP at wire speed (100 Mbps), "
          "the ESP32's tiny 2048-byte network receive buffer instantly overflows, corrupting audio playback. To prevent buffer overflow, "
          "`esp32_manager.py` executes a paced transmission algorithm, breaking the PCM stream into 128-byte chunks and sleeping dynamically "
          "to pace delivery to exactly 8,000 bytes per second:\n"
          "$$\\Delta t_{expected} = \\frac{\\text{Bytes Sent}}{8,000\\text{ Hz}} - t_{elapsed}$$\n"
          "If $\\Delta t_{expected} > 0$, the worker thread sleeps for $\\Delta t_{expected}$, guaranteeing pristine, glitch-free acoustic playback.")

    add_p(doc,
          "Physical Button Interrupt Protocol: The ESP32 firmware monitors a tactile emergency button on GPIO 14 (configured as `INPUT_PULLUP`). "
          "When pressed by ground personnel or flight crew, the pin pulls LOW. The ESP32 debounces the signal and immediately transmits `BTN\\n` "
          "across the established TCP socket. Upon receipt, `esp32_manager.py` executes an asynchronous callback, logging an immediate high-priority "
          "hardware alert on the mission control dashboard.")

    # 4.6 WEBSOCKET TELEMETRY
    add_section_heading(doc, "4.6", "WebSocket Telemetry and Asynchronous State Synchronization")
    add_p(doc,
          "To provide operators with continuous situational awareness, the primary analysis server (`analysis_server.py`, Port 8082) broadcasts "
          "real-time JSON state packets to all connected dashboard browser clients over an asynchronous WebSocket endpoint (`/ws`).")

    add_p(doc,
          "Every 0.5 seconds (2.0 Hz), the server constructs a unified telemetry payload incorporating:\n"
          "• `timestamp`: ISO-8601 UTC timestamp.\n"
          "• `total_people`: Cumulative pedestrian count detected across the current frame.\n"
          "• `grid`: Structural matrix specifying $3\\text{ rows} \\times 4\\text{ columns}$, containing an array of 12 zone objects with their "
          "individual occupancy counts and density classifications (Low, Medium, High, Critical).\n"
          "• `alerts`: Queue of active warning and critical alerts containing zone IDs, threshold messages, and GPS coordinates.\n"
          "• `fps`: Current inference and video processing frame rate.\n"
          "• `source`: Active video feed source ('gopro', 'sample', or 'webcam').\n"
          "• `density_classification`: Global macro-level crowd status ('low', 'moderate', 'elevated', or 'critical').\n"
          "• `esp32`: Real-time hardware status of the acoustic unit, including connection state (`connected: true/false`), client IP, "
          "active audio broadcast label, and the timestamp of the last physical button trigger event.")

    add_figure_placeholder(doc, "4.6",
                           "WebSocket Telemetry and Asynchronous State Synchronization Message Topology",
                           "Diagram illustrating the JSON schema and asynchronous WebSocket broadcast topology connecting the analysis server "
                           "to multiple concurrent web dashboard clients on laptops and tablets.")

    doc.add_page_break()
