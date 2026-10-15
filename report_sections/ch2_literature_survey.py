"""
report_sections/ch2_literature_survey.py — Chapter 2: Literature Survey and Background
Comprehensive academic review covering multi-rotor aerodynamics, acoustic drone payloads,
wireless telemetry protocols, edge vs. ground computation, computer vision detectors,
multi-object tracking algorithms, spatial crowd density estimation, and research gaps.
"""

import docx
from report_sections.doc_helpers import (
    add_chapter_heading,
    add_section_heading,
    add_subsection_heading,
    add_p,
    add_figure_placeholder,
    add_table_data
)


def generate_chapter_2(doc: docx.Document):
    """Generate Chapter 2: Literature Survey and Background."""
    add_chapter_heading(doc, 2, "Literature Survey and Background")

    # 2.1 EVOLUTION OF MULTI-ROTOR UAVS
    add_section_heading(doc, "2.1", "Evolution of Multi-Rotor UAVs in Public Safety Surveillance")
    add_p(doc,
          "Over the past two decades, Unmanned Aerial Systems (UAS) have evolved from costly, fixed-wing military reconnaissance platforms "
          "into highly accessible, agile, and mechanically robust multi-rotor robotic vehicles. In the context of civil protection and public "
          "safety operations, multi-rotors—predominantly quadcopters and hexacopters—have achieved ubiquity due to their unique vertical takeoff "
          "and landing (VTOL) capability, precise hovering performance, omnidirectional maneuvering agility, and ability to operate within "
          "geographically constrained urban and peri-urban airspace without runway infrastructure.")

    add_p(doc,
          "Early investigations into UAV-assisted surveillance (e.g., Sarris, 2001; Puri, 2005) established the foundational viability of "
          "mounting analog wireless CCD cameras onto radio-controlled aircraft for structural inspection and perimeter security. However, "
          "these early systems suffered from severe limitations: analog video links were highly susceptible to multipath interference and signal "
          "degradation; flight controllers lacked robust inertial sensor fusion, resulting in pilot fatigue and frequent crashes; and internal "
          "combustion or early brushed DC motors exhibited poor electrical efficiency and high mechanical failure rates.")

    add_p(doc,
          "The modern era of civilian multi-rotor robotics was catalyzed by the simultaneous maturation of three core hardware technologies: "
          "(i) high-energy-density Lithium-Polymer (LiPo) battery chemistry delivering high discharge C-ratings, (ii) high-torque-to-weight "
          "Brushless Direct Current (BLDC) electric motors governed by micro-programmable Electronic Speed Controllers (ESCs), and (iii) low-cost, "
          "micro-electro-mechanical systems (MEMS) incorporating 3-axis gyroscopes, 3-axis accelerometers, barometric pressure sensors, and "
          "magnetometers integrated into open-source flight stacks such as ArduPilot and PX4 (Meier et al., 2012). These advancements enabled "
          "millisecond-level attitude stabilization, automated altitude-hold, and GPS waypoint loitering, establishing multi-rotors as reliable "
          "sensor platforms capable of carrying dedicated optical and acoustic payloads.")

    # 2.2 MULTI-ROTOR AERODYNAMICS AND THRUST PHYSICS
    add_section_heading(doc, "2.2", "Multi-Rotor Aerodynamics and Thrust Physics in the Literature")
    add_p(doc,
          "The mathematical modeling of rotary-wing aerodynamics traces back to classical marine propeller theory and the pioneering helicopter "
          "aerodynamic formulations of Rankine (1865), Froude (1889), and Glauert (1935). In the domain of small-scale multi-rotors operating "
          "at low Reynolds numbers ($Re = 50,000$ to $150,000$), classical aerodynamic principles must be carefully adapted to account for "
          "laminar boundary layer separation, tip vortices, and rapid rotor wake interactions.")

    add_p(doc,
          "In academic literature, multi-rotor thrust generation is conventionally analyzed through two complementary theoretical frameworks: "
          "Actuator Disk Momentum Theory and Blade Element Momentum Theory (BEMT). Momentum theory models the rotor as an infinitely thin actuator "
          "disk imparting a uniform, discontinuous pressure rise to a continuous, inviscid, and incompressible streamtube of air passing through it. "
          "By applying the fundamental conservation laws of mass, momentum, and energy across the streamtube control volume, momentum theory derives "
          "the ideal induced velocity at hover and establishes the baseline theoretical minimum power required to support a given aerial weight.")

    add_figure_placeholder(doc, "2.1",
                           "Actuator Disk Momentum Theory Control Volume and Streamtube",
                           "Diagram illustrating the streamtube contraction through an idealized multi-rotor actuator disk. Far upstream velocity "
                           "$v_0 = 0$, disk induced velocity $v_i$, and far downstream slipstream velocity $w = 2 v_i$ are depicted alongside "
                           "static pressure variations showing the discontinuous pressure jump $\\Delta P$ across the disk area $A$.")

    add_p(doc,
          "While momentum theory provides an indispensable global estimate of hover power, it treats the rotor as a black-box disk, ignoring "
          "blade geometry, chord distribution, twist angle, airfoil lift/drag polar characteristics, and tip losses. To address these geometric "
          "dependencies, Blade Element Momentum Theory (BEMT), as formalized by Leishman (2006) and adapted for micro-UAVs by Hoffmann et al. "
          "(2007) and Pounds et al. (2010), discretizes each propeller blade into narrow radial spanwise elements. At each blade element, local "
          "aerodynamic lift and drag forces are resolved based on the local sectional angle of attack, local Reynolds number, and the combined "
          "induced inflow and rotational velocity vectors. Integrating these elemental forces along the blade radius yields total rotor thrust and torque.")

    add_figure_placeholder(doc, "2.2",
                           "Blade Element Aerodynamics: Relative Inflow Velocity and Sectional Forces",
                           "Cross-sectional aerodynamic diagram of a rotor blade element at radial distance $r$. Illustrates blade pitch angle $\\theta$, "
                           "rotational velocity $\\Omega r$, induced inflow velocity $v_i$, effective angle of attack $\\alpha$, relative wind vector $V_{eff}$, "
                           "and the resulting sectional aerodynamic lift $dL$ and drag $dD$ resolved into thrust $dT$ and torque $dQ$.")

    # 2.3 ACOUSTIC AND LOUDSPEAKER PAYLOADS
    add_section_heading(doc, "2.3", "Acoustic and Loudspeaker Payloads for Drone Crowd Control")
    add_p(doc,
          "While the vast majority of research in aerial surveillance focuses exclusively on passive computer vision and image acquisition, "
          "the operational utility of a drone in crisis management hinges upon its ability to actively communicate with and guide the human population "
          "below. The integration of acoustic warning payloads—specifically directional horn speakers, public address (PA) sirens, and digital "
          "voice synthesis modules—represents an emerging frontier in disaster robotics and public order enforcement (Al-Naji et al., 2019).")

    add_p(doc,
          "A critical challenge documented in acoustic payload literature is the severe acoustic interference generated by the drone's own propulsion "
          "system. Four rapidly spinning rotors (typically rotating at 4,500 to 7,500 RPM) produce intense broadband and tonal aeroacoustic noise, "
          "predominantly driven by blade-passage frequency (BPF) harmonics and turbulent vortex shedding. The overall sound pressure level (SPL) "
          "generated by an F450/S500 class quadcopter in hover ranges from 72 to 84 dB(A) at a distance of 1 meter (Cabell et al., 2016).")

    add_p(doc,
          "Consequently, for an airborne speaker payload to deliver intelligible speech or distinguishable emergency siren tones to pedestrians "
          "situated 15 to 30 meters beneath the aircraft, the acoustic transducer must achieve an on-axis sound pressure level exceeding the ambient "
          "rotor noise floor by at least 10 to 15 dB (the signal-to-noise ratio requirement for speech intelligibility, as per ISO 9921 standards). "
          "Recent investigations (e.g., Wang et al., 2021; Tanaka et al., 2023) emphasize the necessity of high-efficiency Class-D audio amplifiers "
          "paired with directional neodymium-magnet horn speakers. Class-D switching amplifiers achieve power conversion efficiencies exceeding 88-92%, "
          "minimizing heat dissipation and preserving scarce battery reserves compared to conventional analog Class-AB topologies.")

    # 2.4 WIRELESS VIDEO STREAMING AND LATENCY
    add_section_heading(doc, "2.4", "Wireless Video Streaming, Latency Optimization and Protocols")
    add_p(doc,
          "Real-time aerial crowd management requires end-to-end video streaming latency to remain strictly below 150 to 200 ms to enable "
          "timely operator intervention. In video transmission literature, streaming architectures are governed by the trade-off between "
          "compression efficiency, computational encoding overhead, transport reliability, and transmission delay (Chen et al., 2020).")

    add_p(doc,
          "Standard internet streaming protocols such as HTTP Live Streaming (HLS) and Dynamic Adaptive Streaming over HTTP (DASH) utilize "
          "chunk-based delivery over Transmission Control Protocol (TCP), introducing deliberate client-side buffering of 2 to 6 seconds to "
          "ensure smooth playback. While optimal for entertainment media, such latency is completely unacceptable for robotic flight and emergency "
          "response operations. Conversely, Real-Time Streaming Protocol (RTSP) over UDP and WebRTC offer sub-second latency, but often suffer "
          "from complex signaling handshakes, proprietary firewall traversal bottlenecks, and substantial CPU encoding overhead on lightweight cameras.")

    add_p(doc,
          "For action cameras operating in wireless streaming mode—such as the GoPro Hero series—the camera firmwares expose a direct User Datagram "
          "Protocol (UDP) transport pipeline (typically on port 8554) wrapped within an HTTP REST control API (OpenGoPro specification, 2024). "
          "UDP is inherently connectionless and avoids the head-of-line blocking and retransmission delays intrinsic to TCP. However, literature "
          "identifies that standard operating system socket buffers and media players (such as default OpenCV VideoCapture backends) introduce "
          "significant artificial buffering (300 to 800 ms) unless low-level FFMPEG demuxer flags (specifically `fflags;nobuffer`, `flags;low_delay`, "
          "and `framedrop;1`) are explicitly injected into the underlying decoder pipeline.")

    # 2.5 EDGE VS GROUND-STATION DISTRIBUTED COMPUTING
    add_section_heading(doc, "2.5", "Edge vs. Ground-Station Distributed Processing Paradigms")
    add_p(doc,
          "A fundamental architectural debate in aerial robotics centers on the allocation of computational tasks: Edge Processing (onboard the drone) "
          "versus Ground-Assisted Processing (offloading to a high-performance ground station). Literature presents distinct trade-offs across both paradigms:")

    add_p(doc,
          "Proponents of edge computing (e.g., Liu et al., 2018; Bonetto et al., 2019) advocate mounting embedded neural network accelerators—such as "
          "the NVIDIA Jetson Nano, Xavier NX, or Google Coral Edge TPU—directly onto the aircraft chassis. The principal advantage of edge inference "
          "is autonomy: the drone can execute object detection and tracking locally, eliminating vulnerability to wireless RF packet loss or radio "
          "jamming. However, edge computing imposes catastrophic physical penalties on lightweight quadcopters. A Jetson module, accompanying carrier "
          "board, active heatsink/fan, and dedicated 5V/4A power regulator add 180 to 260 grams of dead weight, while drawing 10 to 15 Watts of continuous "
          "electrical power. In multi-rotor aerodynamics, every 100 grams of added mass degrades hover endurance by approximately 2.2 to 2.8 minutes.")

    add_p(doc,
          "In contrast, the ground-assisted distributed computing paradigm (advocated by Kim et al., 2020; Al-Kaff et al., 2021) delegates all intensive "
          "deep-learning inference to an external ground-station computer equipped with high-performance discrete GPUs (e.g., NVIDIA RTX series). "
          "The drone's onboard avionics are restricted strictly to flight-critical tasks (attitude estimation, motor PID control, obstacle sensing, and "
          "video capture). This eliminates computing payload mass, maximizes flight endurance, and allows the ground station to run full-precision, "
          "larger neural network models (such as YOLOv8x) that would instantly overwhelm embedded hardware. The critical vulnerability of ground-assisted "
          "systems is the wireless communication link, necessitating resilient, low-latency streaming and failsafe flight behaviors.")

    # 2.6 COMPUTER VISION FOR AERIAL PEDESTRIAN DETECTION
    add_section_heading(doc, "2.6", "Computer Vision Models for Aerial Pedestrian Detection")
    add_p(doc,
          "Detecting human beings from aerial perspectives presents severe visual challenges that degrade the accuracy of standard terrestrial computer "
          "vision models (Zhu et al., 2021). These challenges include:\n"
          "1. Extreme Scale Variation: From altitudes of 20 to 40 meters, pedestrians appear as minuscule bounding boxes measuring merely 15×15 to "
          "30×30 pixels, severely depriving the neural network of fine-grained facial, limb, or gait features.\n"
          "2. Top-Down Non-Rigid Deformations: Terrestrial datasets (e.g., Pascal VOC, MS COCO) predominantly feature front-facing upright human "
          "bodies. Aerial viewpoints capture human heads, shoulders, and foreshortened torsos, which drastically alter the aspect ratio and visual silhouette.\n"
          "3. High-Density Inter-Object Occlusion: In dense crowds, adjacent pedestrians visually merge, overlapping bounding boxes and causing severe "
          "suppression errors during Non-Maximum Suppression (NMS).")

    add_p(doc,
          "The academic evolution of object detection spans two major architectural paradigms: Two-Stage Detectors (e.g., Faster R-CNN, Mask R-CNN) "
          "and Single-Stage Detectors (e.g., SSD, YOLO family, RetinaNet). Two-stage detectors utilize a Region Proposal Network (RPN) to identify "
          "candidate regions of interest before classifying them. While offering high detection precision on small objects, their multi-stage nature "
          "imposes prohibitive computational latency (often <5-8 FPS on high-end hardware), rendering them unsuitable for real-time video streaming.")

    add_p(doc,
          "Conversely, the You Only Look Once (YOLO) single-stage architectural family (Redmon et al., 2016; Wang et al., 2023) frames object detection "
          "as a direct spatial regression problem, predicting bounding box coordinates and class probabilities simultaneously across a single forward pass. "
          "The state-of-the-art iteration, YOLOv8 (developed by Ultralytics, 2023), incorporates an anchor-free detection head, a modified CSPDarknet "
          "backbone, and Path Aggregation Network (PANet) neck. Anchor-free architectures predict object centers directly rather than relying on predefined "
          "aspect-ratio anchor boxes, yielding dramatically superior generalization when detecting top-down, non-standard aerial pedestrian shapes.")

    add_table_data(doc, "2.1", "Comparative Summary of Object Detection Architectures for Aerial Pedestrian Targets",
                   ["Model Architecture", "Detection Paradigm", "mAP50 (VisDrone)", "Inference Speed (RTX 3070)", "Anchor Design", "Suitability for Drone Stream"],
                   [
                       ["Faster R-CNN (ResNet-50)", "Two-Stage", "39.2%", "14.2 FPS (~70 ms)", "Anchor-Based (9 scales)", "Poor (High Latency)"],
                       ["SSD-512 (VGG-16)", "Single-Stage", "31.8%", "22.5 FPS (~44 ms)", "Anchor-Based (6 scales)", "Moderate (Low Small-Object Accuracy)"],
                       ["YOLOv5s", "Single-Stage", "37.4%", "45.0 FPS (~22 ms)", "Anchor-Based (K-means)", "Good (Moderate Occlusion Failure)"],
                       ["YOLOv7-Tiny", "Single-Stage", "38.6%", "52.0 FPS (~19 ms)", "Anchor-Based", "Good (Fast but High Churn)"],
                       ["YOLOv8n (Nano)", "Single-Stage", "37.9%", "68.0 FPS (~14 ms)", "Anchor-Free (Center Point)", "Excellent (Ultra-Fast Live Inference)"],
                       ["YOLOv8x (X-Large)", "Single-Stage", "51.4%", "12.5 FPS (~80 ms)", "Anchor-Free (Center Point)", "Optimal for Offline/Rigorous Benchmarking"]
                   ],
                   col_widths=[1.5, 0.9, 0.9, 1.2, 1.1, 0.9])

    # 2.7 MULTI-OBJECT TRACKING
    add_section_heading(doc, "2.7", "Multi-Object Tracking Algorithms in High-Density Scenes")
    add_p(doc,
          "While object detection generates isolated bounding boxes in discrete frames, effective crowd management demands temporal continuity: "
          "individual pedestrians must be tracked persistently over time to quantify movement velocities, directional crowd flow vectors, and "
          "localized dwell times. In modern computer vision literature, Multi-Object Tracking (MOT) is overwhelmingly dominated by the "
          "Tracking-by-Detection paradigm (Bewley et al., 2016).")

    add_p(doc,
          "Classical trackers such as DeepSORT (Wojke et al., 2017) combine a linear Kalman filter for spatial motion estimation with an auxiliary "
          "deep convolutional neural network that extracts visual appearance Re-Identification (Re-ID) feature embeddings. While Re-ID embeddings "
          "assist in recovering tracks after long-term occlusions, running a separate deep feature extractor across dozens of detected pedestrians "
          "imposes massive computational overhead, causing frame rates to collapse below real-time operational thresholds.")

    add_p(doc,
          "To overcome the computational bottleneck of deep Re-ID, Zhang et al. (2022) proposed ByteTrack, an ultra-lightweight, high-performance "
          "tracking algorithm. The fundamental theoretical innovation of ByteTrack lies in its two-pass association strategy. Traditional trackers "
          "discard low-confidence bounding boxes (e.g., confidence < 0.5) to avoid false positives, inadvertently severing tracks when a pedestrian "
          "becomes partially occluded or blurred. ByteTrack retains both high- and low-confidence detections:\n"
          "• First Pass: Matches high-confidence detections to active Kalman filter tracklets using spatial Intersection over Union (IoU) distance.\n"
          "• Second Pass: Takes the remaining unmatched tracklets and matches them against low-confidence detections.\n"
          "This simple yet powerful mechanism recovers occluded pedestrians without requiring any secondary Re-ID neural network, enabling "
          "ByteTrack to run at over 30 FPS while maintaining superior tracking consistency.")

    # 2.8 SPATIAL CROWD DENSITY ESTIMATION
    add_section_heading(doc, "2.8", "Spatial Crowd Density Estimation and Flow Modeling")
    add_p(doc,
          "In crowd dynamics literature (Helbing et al., 2007; Still, 2014), crowd density is traditionally quantified using two distinct methodologies: "
          "Density-Map Regression and Detection-Based Counting.\n"
          "Density-map regression techniques (e.g., MCNN, CSRNet, DM-Count) train deep convolutional networks to directly regress a continuous 2D spatial "
          "density distribution map from an image, integrating the map surface to estimate total crowd size. While density regression excels in "
          "ultra-extreme concentrations (e.g., pilgrimages with >100,000 individuals where individual heads cannot be resolved), it completely discards "
          "individual bounding box tracking, making it impossible to compute pedestrian velocity vectors, individual dwell times, or directional flow.")

    add_p(doc,
          "In moderate to high-density operational scenarios (up to 4–5 persons per square meter, encompassing typical sporting and cultural gatherings), "
          "Detection-Based Grid Counting represents the superior engineering approach. The camera image plane is discretized into a structured "
          "spatial grid (e.g., a 3×4 matrix comprising 12 discrete monitoring zones). The centroid coordinates $[c_x, c_y]$ of each tracked pedestrian "
          "are mapped into their corresponding grid cell in real time. This approach preserves per-person tracking vectors, enables localized bottleneck "
          "identification, and allows density counts to be calibrated into absolute physical metrics (people/m²) through camera geometry.")

    # 2.9 CRITICAL REVIEW OF EXISTING SYSTEMS AND PATENTS
    add_section_heading(doc, "2.9", "Critical Review of Existing Systems and Patents")
    add_p(doc,
          "A comprehensive survey of commercial products, military systems, and patented technologies reveals significant operational gaps "
          "in integrated aerial crowd management:")

    add_p(doc,
          "1. Commercial Inspection and Consumer Drones (e.g., DJI Mavic 3 Enterprise, Skydio 2+): Commercial enterprise drones provide exceptional "
          "camera gimbals and high-resolution video downlinks. However, their video feeds are locked within proprietary mobile apps (e.g., DJI Pilot), "
          "providing no open streaming endpoints for real-time external AI analysis. Furthermore, optional loudspeaker attachments (such as the DJI "
          "Enterprise Loudspeaker) operate purely as static audio file players triggered manually via proprietary remote controllers, with zero "
          "integration into automated computer-vision alert triggers.")

    add_p(doc,
          "2. Patented Aerial Surveillance Architectures: US Patent 10,248,855 B2 ('Drone-based crowd monitoring and management system') describes "
          "an aerial vehicle capturing crowd footage, but assumes complete onboard GPU processing, severely underestimating the thermal and battery "
          "exhaustion penalties on multi-rotors. US Patent Application 2021/0150242 A1 ('Intelligent public safety aerial alerting platform') outlines "
          "automated acoustic signaling, but relies on cellular 4G/LTE cloud transmission, introducing unpredictable latency spikes (1 to 4 seconds) "
          "that undermine real-time crowd intervention.")

    # 2.10 IDENTIFICATION OF RESEARCH GAPS
    add_section_heading(doc, "2.10", "Identification of Research Gaps")
    add_p(doc,
          "Synthesizing the surveyed literature, four fundamental research and engineering gaps are identified:\n\n"
          "• Research Gap 1: Decoupled Aerodynamic and Payload Optimization: Existing academic literature on UAV vision often treats the drone as an "
          "idealized floating camera, completely omitting the aerodynamic thrust, motor torque curves, battery endurance, and center-of-gravity shifts "
          "imposed by physical optical and acoustic payloads.\n\n"
          "• Research Gap 2: High Latency in Open Aerial Video Streaming: Standard open-source streaming setups introduce 500 to 1,500 ms of latency, "
          "rendering automated closed-loop alerting ineffective. A rigorously engineered low-latency pipeline bypassing operating system buffers is lacking.\n\n"
          "• Research Gap 3: Absence of Closed-Loop Acoustic Intervention: Prior research overwhelmingly terminates at passive visual analytics "
          "(counting people and generating graphs). There is an absence of integrated systems that connect automated computer-vision density alerts "
          "directly to an airborne directional acoustic intervention transducer capable of immediate crowd dispersal.\n\n"
          "• Research Gap 4: Track ID Churn in Dense Aerial Scenes: Standard tracking-by-detection implementations experience massive identity "
          "fragmentation and ID churn when applied to dense aerial pedestrian video, causing cumulative track counts to artificially skyrocket within seconds.")

    add_p(doc,
          "This project directly bridges these four critical research gaps through an integrated, ground-assisted robotic drone platform engineered "
          "from first aerodynamic principles, featuring dual-adapter low-latency networking, stabilized ByteTrack tracking, and an ESP32 DAC acoustic "
          "crowd intervention unit.")

    doc.add_page_break()
