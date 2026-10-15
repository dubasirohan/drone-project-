"""
report_sections/ch8_conclusion_future.py — Chapter 8: Conclusion and Future Work.
Synthesizes engineering contributions, articulates critical operational limitations,
and establishes a concrete technical roadmap for autonomous repositioning,
edge NPU acceleration, and multi-drone cooperative surveillance.
"""

import docx
from report_sections.doc_helpers import (
    add_chapter_heading,
    add_section_heading,
    add_p
)


def generate_chapter_8(doc: docx.Document):
    """Generate Chapter 8: Conclusion and Future Work."""
    add_chapter_heading(doc, 8, "Conclusion and Future Work")

    # 8.1 SUMMARY OF CONTRIBUTIONS
    add_section_heading(doc, "8.1", "Summary of Contributions")
    add_p(doc,
          "This thesis has designed, mathematically modeled, aerodynamically sized, and physically implemented a distributed, "
          "ground-assisted aerial robotic drone platform for real-time crowd management, density monitoring, and acoustic intervention. "
          "Addressing the lethal risks of compressive stampedes and pedestrian bottlenecks in mass public gatherings, the project successfully "
          "bridges the gap between passive visual surveillance and active crisis intervention.")

    add_p(doc,
          "The core technical accomplishments and contributions delivered in this work include:\n\n"
          "1. Aerodynamic and Propulsion Sizing from First Principles: Formulated a rigorous momentum theory and Blade Element Momentum Theory "
          "(BEMT) aerodynamic model for multi-rotor hover flight. Sized high-torque ReadyToSky 2216 880KV brushless DC motors paired with 1045 "
          "glass-filled nylon propellers and 30A SimonK ESCs powered by a 4S 14.8V 5200 mAh Lithium-Polymer battery. Dynamometer testing verified "
          "a combined peak thrust of 3,840 gf against an All-Up Weight (AUW) of 1,680 gf, delivering an optimal Thrust-to-Weight Ratio of 2.28:1 "
          "and an experimental hover endurance of 17.8 minutes (matching the 18.05-minute theoretical prediction within 1.38%).\n\n"
          "2. Structural Airframe and Payload Weight Engineering: Evaluated F450, S500, and Tarot 650 airframe options, selecting the S500 platform "
          "for its 10° upward arm dihedral, internal carbon fiber arm stiffeners, and 165 mm ground clearance. Successfully integrated a dual-payload "
          "system comprising an ultra-high-definition GoPro Hero 13 optical acquisition system (190 g with vibration-isolated bracket) and a custom "
          "ESP32 crowd management acoustic unit (130 g) featuring an 8Ω 5W horn speaker driven by a Class-D amplifier through built-in DAC Channel 1 "
          "(GPIO 25) with an active-LOW emergency hardware trigger (GPIO 14).\n\n"
          "3. Center of Gravity Alignment and Vibration Isolation: Mathematically balanced the three-dimensional Center of Gravity ($x_{cg} = 0.0\\text{ mm}, "
          "y_{cg} = 0.0\\text{ mm}, z_{cg} = +12.91\\text{ mm}$), utilizing the underslung payloads to lower the vertical CG and impart pendulum flight "
          "stability. Designed a 40-Durometer silicone damping system that attenuates 95.7% of high-frequency motor vibrations at 88 Hz, eliminating "
          "camera jello effects and IMU DC gyro bias drift.\n\n"
          "4. Dual-Adapter Low-Latency Networking Topology: Decisively eliminated the single-adapter wireless streaming bottleneck by establishing a dual "
          "network interface architecture on the ground station. Adapter 1 connects directly to the GoPro's Access Point (`10.5.5.9`) via unbuffered "
          "UDP streaming on port 8554 (achieving 102 ms glass-to-glass latency), while Adapter 2 bridges ground telemetry, the ESP32 TCP socket "
          "server (port 8002), and the web mission control dashboard without packet contention.\n\n"
          "5. Deep Learning Detection and Track ID Churn Resolution: Deployed single-stage YOLOv8 convolutional detection on the ground station GPU "
          "(14.2 ms inference for YOLOv8n; 86.0 ms for YOLOv8x validation). Integrated ByteTrack multi-object tracking and successfully resolved "
          "the pervasive 'Track ID Churn' malfunction in dense aerial crowds by elevating the confidence floor from 0.10 to 0.25 and doubling the "
          "Kalman track buffer, achieving an 81.0% reduction in fragmented identities (stabilizing active IDs at 54 across a 43-person benchmark clip).\n\n"
          "6. 3×4 Spatial Grid Partitioning and Pinhole Georeferencing: Discretized aerial video frames into 12 localized spatial zones, computing "
          "per-zone pedestrian densities categorized into Low, Moderate, High, and Critical bands. Formulated a calibrated pinhole camera ray-plane "
          "intersection model that translates image-space pixel centroids into geographic GPS coordinates using ArduPilot flight telemetry.\n\n"
          "7. Automated Closed-Loop Acoustic Intervention: Engineered an active audio streaming pipeline driving the airborne ESP32 speaker. "
          "Fast-path mathematical synthesizers deliver 0.2 ms instant emergency sirens and attention chimes, complemented by a multilingual "
          "Google TTS engine supporting 7 regional languages. Experimental acoustic testing verified 71.4 dB(A) output at 20 meters, achieving an "
          "end-to-end closed-loop reaction time of 145.4 milliseconds.\n\n"
          "8. Responsive Mission Control Web Dashboard: Constructed a single-page dark-themed operations dashboard (`index.html`) serving live video "
          "with dynamic canvas grid overlays, real-time population trend charts, spatial heatmaps, interactive ESP32 acoustic controls, and a "
          "one-click demo video looping engine for offline evaluation.")

    # 8.2 LIMITATIONS AND CRITICAL INSIGHTS
    add_section_heading(doc, "8.2", "Limitations and Critical Insights")
    add_p(doc,
          "Despite the successful realization and validation of the integrated robotic system, several engineering constraints and operational "
          "limitations were identified during experimental testing:\n\n"
          "1. RF Transmission Range and Wi-Fi Congestion: The system's video and telemetry links operate over standard 2.4 GHz and 5.8 GHz IEEE 802.11 "
          "Wi-Fi channels. In dense mass gathering environments where thousands of personal smartphones generate intense RF noise floor elevation, "
          "reliable transmission range is constrained to approximately 150 to 200 meters line-of-sight. Extending range beyond 500 meters will require "
          "migrating to dedicated OFDM digital video datalinks (e.g., SIYI HM30 or Herelink) operating on licensed frequencies.\n\n"
          "2. Acoustic Projection Limits at High Altitudes: While the 8Ω 5W horn speaker provides exceptional clarity at 15–20 meters (71.4 dB SPL, "
          "+9.4 dB SNR over hover noise), its acoustic authority degrades to +4.8 dB SNR at altitudes exceeding 30 meters. In extremely loud crowd "
          "environments (e.g., stadium cheers >80 dB), higher-power acoustic transducers (15–25W) with neodymium compression drivers will be required.\n\n"
          "3. Environmental and Weather Susceptibility: The S500 quadcopter frame, exposed ESCs, and open motor bell housings are not IP-rated against "
          "water ingress. Operations are restricted to fair weather, with flight strictly prohibited during precipitation or sustained wind speeds "
          "exceeding 10.0 m/s (36 km/h).\n\n"
          "4. Hover Endurance Horizon: While 17.8 minutes of hover endurance successfully covers tactical intervention flights, continuous monitoring "
          "of multi-hour public events requires a rotational fleet of at least three aircraft paired with rapid battery hot-swapping or autonomous "
          "contactless charging pads.")

    # 8.3 FUTURE WORK AND ROADMAP
    add_section_heading(doc, "8.3", "Future Work and Roadmap")
    add_p(doc,
          "Building upon the foundational architecture established in this thesis, future research and development will target four specialized frontiers:\n\n"
          "1. Autonomous Reactive Repositioning via MAVLink GUIDED Mode: In the current implementation, the ground station estimates the GPS coordinates "
          "of critical crowd zones and presents them to the human pilot. Future iterations will establish an autonomous MAVLink bridge using `pymavlink` "
          "or DroneKit. When a Critical alert is confirmed, the system will programmatically command the Pixhawk autopilot to transition into GUIDED mode, "
          "automatically flying the quadcopter directly to the congested sector's GPS coordinates and loitering at 15 meters to project acoustic warnings.\n\n"
          "2. Ultra-Low-Power Edge Neural Acceleration: As ultra-efficient edge Neural Processing Units (NPUs)—such as the Hailo-8 M.2 module (26 TOPS "
          "at 2.5W) or Raspberry Pi AI Kit—mature, the entire YOLOv8 detection and ByteTrack pipeline can be migrated directly onboard the drone without "
          "mass or power penalties. This will enable true autonomous swarm operation independent of ground-station communication links.\n\n"
          "3. Active 2-Axis Brushless Gimbal Integration: Replacing the fixed 3D-printed camera bracket with an ultra-lightweight (65 g) 2-axis brushless "
          "direct-drive gimbal running SimpleBGC or Storm32 firmware will decouple camera pointing from aircraft pitch and roll attitudes, enabling "
          "nadir (straight down) tracking during aggressive flight maneuvers.\n\n"
          "4. Multi-UAV Cooperative Swarm Telemetry: Developing a decentralized Robot Operating System (ROS 2) communications mesh enabling multiple "
          "quadcopters to collaboratively partition large public events. One high-altitude drone can maintain macro-scale perimeter density mapping "
          "while two low-altitude tactical drones dynamically reposition to provide localized acoustic crowd dispersal.")

    doc.add_page_break()
