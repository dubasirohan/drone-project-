"""
report_sections/ch1_introduction.py — Chapter 1: Introduction
Comprehensive introduction covering background context, crowd dynamics hazards,
robotics-assisted intervention, problem formulation, objectives, scope boundaries,
risk analysis, ethical governance, and individual contributions.
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


def generate_chapter_1(doc: docx.Document):
    """Generate Chapter 1: Introduction."""
    add_chapter_heading(doc, 1, "Introduction")

    # 1.1 OVERVIEW AND BACKGROUND CONTEXT
    add_section_heading(doc, "1.1", "Overview and Background Context")
    add_p(doc,
          "The rapid pace of global urbanization, coupled with expanding populations and the scale of mass socio-cultural, religious, "
          "sporting, and civic gatherings, has made mass crowd management an extraordinarily complex public safety challenge. "
          "Events such as major marathons, political rallies, pilgrimage routes, transit hubs, and music festivals regularly congregate tens "
          "of thousands of individuals into geographically constrained pedestrian corridors. Under such high spatial concentrations, "
          "crowd dynamics undergo a phase transition from free-flowing laminar motion to turbulent, highly compressed non-Newtonian flow. "
          "In these compressed environments, localized shockwaves, bottleneck congestion, and sudden panic surges can precipitate deadly "
          "crushes or progressive crowd collapse (often erroneously termed stampedes), resulting in catastrophic loss of human life.")

    add_p(doc,
          "Traditionally, municipal authorities, law enforcement agencies, and event security personnel have relied on static closed-circuit "
          "television (CCTV) cameras mounted on lampposts, building facades, and perimeter fences. While fixed optical surveillance offers "
          "continuous monitoring of predefined checkpoints, its operational effectiveness is severely compromised by fixed blind spots, "
          "susceptibility to physical occlusion in dense foliage or architectural canyons, and an inherent inability to dynamically track "
          "evolving spatial patterns. Furthermore, ground-level security patrols possess severely restricted visual horizons and struggle "
          "to perceive macro-level bottlenecks developing merely a few hundred meters ahead within an elevated crowd.")

    add_p(doc,
          "In response to these critical limitations, Unmanned Aerial Vehicles (UAVs)—commonly designated as drones—have emerged as a "
          "transformational robotic paradigm in modern security operations. Operating from elevated perspectives (15 to 50 meters above ground level), "
          "a multi-rotor robotic platform provides an unhindered, flexible, and comprehensive macro-scale field of view. Unlike fixed surveillance "
          "installations, an aerial drone can rapidly reposition across complex three-dimensional terrain, dynamically track moving crowd boundaries, "
          "and loiter above critical ingress/egress corridors.")

    add_p(doc,
          "However, deploying an autonomous or semi-autonomous multi-rotor platform for active crowd management introduces formidable engineering "
          "and robotics challenges. Foremost among these are the severe mechanical, aerodynamic, and electrical constraints imposed by payload "
          "capacities, battery energy density, and hover flight endurance. Unlike passive reconnaissance aircraft, an operational crowd-intervention "
          "drone must carry both high-resolution optical acquisition sensors (such as wide-angle 4K cameras) and active acoustic intervention "
          "mechanisms (such as directional horn speakers driven by digital audio microcontrollers) to issue timely guidance instructions to "
          "pedestrians. This dual-payload requirement imposes significant mass and aerodynamic drag penalties, demanding meticulous aerodynamic "
          "modeling, propulsion optimization, and weight-budget engineering.")

    # 1.2 MOTIVATION
    add_section_heading(doc, "1.2", "Motivation: Aerial Robotics in Crowd Disasters")
    add_p(doc,
          "The historical record of mass casualty crowd incidents worldwide—from the 2015 Mina pilgrimage disaster in Mecca claiming over "
          "2,000 lives to the 2022 Itaewon Halloween crush in Seoul where 159 young individuals perished in a narrow 3.2-meter-wide alley—demonstrates "
          "that human surveillance alone consistently fails to identify dangerous compressive density thresholds before catastrophic physical contact "
          "occurs. Research in pedestrian physics reveals that once crowd density exceeds 4 to 5 persons per square meter, interpersonal physical contact "
          "becomes continuous, transferring lateral shockwaves through the human mass and stripping individuals of self-volition. At densities exceeding "
          "6 persons per square meter, compressive asphyxiation occurs rapidly even without individuals falling to the ground.")

    add_p(doc,
          "Crucially, in nearly every documented disaster, the underlying congestion developed gradually over 15 to 45 minutes, yet went unnoticed "
          "by ground security personnel until emergency calls were placed. Furthermore, once an alert is raised, ground responders frequently find "
          "themselves trapped along the periphery of the crowd, unable to communicate auditory directions or establish designated dispersal vectors.")

    add_p(doc,
          "These sobering realities provide the fundamental motivation for this project. An aerial robotic system equipped with real-time computational "
          "vision and an active acoustic broadcast mechanism bridges the critical situational awareness and intervention gap. By flying overhead, "
          "the drone continuously evaluates spatial density distributions, detects developing congestion before pressure builds, estimates real-world "
          "geographic coordinates, and immediately delivers audible dispersal commands, attention chimes, or evacuation tones directly over the "
          "congested sector. This shifts crowd management from reactive crisis response to proactive, preventative spatial regulation.")

    add_figure_placeholder(doc, "1.1",
                           "System Architecture Overview: Aerial Subsystem, Ground Station, and Monitoring Dashboard",
                           "Schematic showing the multi-tier distributed ground-assisted architecture. The aerial quadcopter carrying the GoPro Hero 13 "
                           "and ESP32 speaker transmits live video and telemetry over dual wireless links to the ground station laptop, where YOLOv8 "
                           "detection, ByteTrack tracking, 3x4 grid density estimation, and rule-based alert generation occur, culminating in operator "
                           "visualization and acoustic intervention commands via an interactive dashboard.")

    # 1.3 PROBLEM STATEMENT
    add_section_heading(doc, "1.3", "Problem Statement")
    add_p(doc,
          "Existing crowd monitoring systems are characterized by fragmented architectures: commercial consumer drones provide aerial video "
          "recording but lack real-time automated intelligence and onboard crowd-dispersal mechanisms; dedicated intelligent video surveillance "
          "platforms rely on fixed CCTV cameras with constrained blind spots; and academic crowd counting models frequently demand massive "
          "GPU workstations incompatible with lightweight aerial payloads, while offering no direct mechanism to actively intervene during an "
          "unfolding emergency.")

    add_p(doc,
          "Specifically, the fundamental engineering problem addressed in this work can be formulated as follows:\n"
          "How can a multi-rotor robotic aerial platform be aerodynamically modeled, structured, and integrated with a dual visual/acoustic "
          "payload (GoPro Hero 13 optical sensor and an ESP32 DAC-driven crowd speaker) within strict mass (under 1.7 kg All-Up Weight) and power "
          "constraints to achieve sustained hover endurance (>15 minutes), while executing ultra-low-latency wireless video transmission (~100 ms) "
          "and automated ground-assisted crowd density estimation, tracking, and instant acoustic dispersal intervention?")

    # 1.4 OBJECTIVES
    add_section_heading(doc, "1.4", "Objectives of the Project")
    add_p(doc,
          "To resolve the formulated problem statement, this project establishes the following ten specific technical objectives:")

    objectives = [
        "1. Aerodynamic and Propulsion Sizing: Formulate a rigorous momentum theory and Blade Element Momentum Theory (BEMT) model "
        "to calculate thrust requirements, evaluate airframe alternatives (F450 vs. S500 vs. Tarot 650), size brushless motors, match propeller "
        "aerodynamics, and determine Lithium-Polymer battery capacity to guarantee a Thrust-to-Weight Ratio (TWR) exceeding 2.0:1.",

        "2. Dual-Payload Hardware Integration: Design, balance, and mechanically integrate a dual-payload system comprising an ultra-high-definition "
        "GoPro Hero 13 camera (190 g with vibration-isolated bracket) and a custom ESP32 acoustic crowd management speaker unit (130 g) powered "
        "through an integrated step-down regulator.",

        "3. Distributed Ground-Assisted Architecture: Implement a distributed edge-ground computational architecture that decouples flight-critical "
        "stabilization and navigation (executed onboard via Pixhawk/ArduPilot) from computationally intensive deep-learning inference (executed on the ground station).",

        "4. Ultra-Low Latency Video Link: Engineer a dual-adapter wireless communication pipeline utilizing a dedicated direct Wi-Fi UDP stream "
        "to the GoPro Access Point (10.5.5.9) paired with FFMPEG buffer bypass tuning to achieve sub-100 ms live video ingestion on the ground station.",

        "5. Wireless Acoustic Intervention Protocol: Develop an asynchronous TCP socket audio bridge (port 8002) to stream 8000 Hz 8-bit unsigned "
        "PCM audio packets using custom binary framing (0xA5 0x5A header) directly into the ESP32 built-in DAC (GPIO 25), enabling synthetic sirens, "
        "alert chimes, and multilingual text-to-speech dispersal announcements.",

        "6. Deep Learning Person Detection: Implement and empirically evaluate single-stage YOLOv8 convolutional detectors (comparing Nano, Small, "
        "Medium, Large, and X-Large models) to accurately detect pedestrians from top-down aerial perspectives under varying lighting and occlusion.",

        "7. Multi-Object Tracking & ID Churn Reduction: Integrate ByteTrack tracking-by-detection using Kalman filter state estimation and two-pass "
        "matching, systematically diagnosing and eliminating track ID churn in dense crowds by tuning association thresholds and track buffers.",

        "8. Spatial Density Partitioning: Formulate a 3×4 dynamic grid framework to discretize video frames into 12 localized spatial zones, "
        "computing per-zone pedestrian counts and classifying spatial crowd density into Low, Medium, High, and Critical thresholds.",

        "9. Georeferencing & Localization: Establish a pinhole camera geometric projection model that maps image-space pixel centroids of congested "
        "zones to approximate Earth GPS coordinates using drone altitude, attitude (pitch/roll/yaw), and lens field-of-view geometry.",

        "10. Mission Control Operations Dashboard: Construct a single-page, real-time web dashboard serving live video with canvas grid overlays, "
        "real-time zone heatmaps, telemetry indicators, interactive ESP32 acoustic broadcast triggers, and a one-click sample footage demo loop mode."
    ]
    for obj in objectives:
        add_p(doc, obj, space_after=3)

    # 1.5 SCOPE OF THE PROJECT
    add_section_heading(doc, "1.5", "Scope of the Project (In-Scope & Out-of-Scope)")
    add_p(doc,
          "Establishing precise operational boundaries is essential for the rigorous validation of an academic engineering thesis. "
          "The scope of this project is formally delineated into in-scope and out-of-scope boundaries as follows:")

    add_subsection_heading(doc, "1.5.1", "In-Scope Research and Implementation Boundaries")
    in_scope_items = [
        "• Quadcopter airframe assembly, propulsion sizing, wiring, and avionics configuration using Pixhawk 2.4.8 and ArduPilot.",
        "• Mechanical design and fabrication of underslung vibration-damped mounting assemblies for the GoPro Hero 13 and ESP32 speaker.",
        "• Implementation of a dual-adapter ground-station network topology separating high-bandwidth camera UDP streams from telemetry.",
        "• Real-time video ingestion, transcoding, and low-latency MJPEG preview broadcasting.",
        "• Custom binary TCP audio protocol on port 8002 driving the ESP32 DAC channel 1 (GPIO 25) with physical button interrupts (GPIO 14).",
        "• Ground-station person detection utilizing YOLOv8 and multi-object tracking utilizing ByteTrack.",
        "• Grid-based spatial density calculation across a 3×4 matrix (12 discrete zones) with automated threshold alert classification.",
        "• Pinhole camera geometric projection transforming pixel coordinates to approximate GPS coordinates using flight telemetry.",
        "• Web-based mission control operations center featuring live video overlays, zone heatmaps, and audio broadcast controls.",
        "• One-click source switching enabling seamless toggling between live GoPro, laptop webcam, and offline looping aerial test clips."
    ]
    for item in in_scope_items:
        add_p(doc, item, space_after=2)

    add_subsection_heading(doc, "1.5.2", "Out-of-Scope Delimitations")
    out_scope_items = [
        "• Full autonomous navigation in GPS-denied environments: The drone utilizes GPS-assisted flight modes (Loiter, AltHold, Guided) with manual RC override, but does not execute GPS-denied indoor SLAM.",
        "• Facial recognition, biometric profiling, or personal identification: The vision pipeline strictly outputs anonymized bounding boxes and aggregate density statistics; individual tracking IDs are session-ephemeral.",
        "• Definitive stampede prediction: While the system identifies abnormal compressive density and directional bottlenecking, chaotic behavioral stampede prediction remains beyond current physical modeling capabilities.",
        "• Multi-drone swarm coordination: The system is designed for a single aerial platform communicating with a dedicated ground station.",
        "• Unregulated real-world commercial deployment: All physical flight testing is restricted to authorized campus flight test areas following civil aviation guidelines."
    ]
    for item in out_scope_items:
        add_p(doc, item, space_after=2)

    # 1.6 FEASIBILITY AND RISK ANALYSIS
    add_section_heading(doc, "1.6", "Feasibility and Technical Risk Analysis")
    add_p(doc,
          "The technical, operational, and financial feasibility of the proposed drone crowd management system was rigorously assessed "
          "prior to hardware fabrication and code implementation. Key feasibility domains and risk mitigation strategies are detailed below:")

    risk_headers = ["Risk Domain", "Specific Technical Hazard", "Severity", "Engineered Mitigation Strategy"]
    risk_rows = [
        ["Aeronautical / Propulsion", "Motor overheating or insufficient thrust-to-weight ratio leading to sluggish flight control and vortex ring state.", "High",
         "Formulated BEMT and momentum theory calculations; selected high-torque 2216 880KV motors with 1045 propellers delivering 3,840 gf peak thrust against a 1,680 gf AUW (TWR = 2.28:1)."],

        ["Electrical / Power", "Sudden voltage sag under motor acceleration brownout-resetting the Pixhawk flight controller or ESP32 payload.", "Critical",
         "Separated avionics power using dedicated 5.3V 3A switching Power Module from battery tap; added secondary LC low-pass filter and high-C LiPo battery (35C burst)."],

        ["RF / Telemetry Link", "Wi-Fi bandwidth contention between GoPro 1080p video stream and ground station controls causing telemetry freeze.", "High",
         "Implemented Dual-Adapter network separation: Wi-Fi Adapter 1 locked to GoPro 10.5.5.9 direct AP; Wi-Fi Adapter 2 locked to ground hotspot for ESP32 and dashboard."],

        ["Computer Vision", "Small scale of pedestrians (15–30 px) from 25 m altitude causing severe false negatives in dense crowd zones.", "Medium",
         "Evaluated YOLOv8x on 1920x1080 frames with anchor-free head; tuned confidence thresholds from 0.10 to 0.25 to eliminate boundary flicker; utilized ByteTrack second-pass association."],

        ["Tracking ID Churn", "Frequent occlusions and low-confidence detections causing tracking IDs to jump to >100 within 2 seconds for 43 people.", "Medium",
         "Diagnosed root cause as detection noise; increased track_buffer from 30 to 60 frames and enforced IoU matching threshold of 0.7, stabilizing active IDs to 54 across entire test clip."],

        ["Regulatory / Safety", "Flyaway or propeller strike injury during low-altitude crowd loitering.", "Critical",
         "Configured ArduPilot hardware geofencing, automatic Return-to-Launch (RTL) on battery voltage <14.0V or RC signal loss, and instant hardware RC manual override on FlySky FS-i6."]
    ]
    add_table_data(doc, "1.1", "Comprehensive Technical Feasibility and Risk Mitigation Matrix", risk_headers, risk_rows,
                   col_widths=[1.2, 1.8, 0.8, 2.7])

    # 1.7 ETHICAL SAFEGUARDS AND PRIVACY GOVERNANCE
    add_section_heading(doc, "1.7", "Ethical Governance, Privacy and Regulatory Compliance")
    add_p(doc,
          "The deployment of aerial robotic platforms over human populations inevitably intersects with civil liberties, privacy rights, "
          "and public safety ethics. This system was designed in strict accordance with the 'Privacy by Design' framework and adheres to "
          "the Directorate General of Civil Aviation (DGCA) drone operational regulations in India.")

    add_p(doc,
          "1. Non-Biometric Anonymization: The vision pipeline operates solely at the spatial occupancy level. No facial recognition, "
          "gait biometric profiling, demographic tagging, or identity matching algorithms are incorporated or enabled. Bounding boxes record "
          "only bounding coordinates [x1, y1, x2, y2] and class index 0 (Person).")

    add_p(doc,
          "2. Ephemeral In-Memory Processing: Video frames streamed from the drone are processed directly in system memory buffers and immediately "
          "discarded after analysis. No persistent photographic or biometric records of pedestrians are stored to permanent disk media, preventing "
          "surveillance creep or data breach hazards.")

    add_p(doc,
          "3. Human-in-the-Loop Authority: While the ground station automates density threshold calculations and visualizes emergency alerts, "
          "all critical command decisions—including triggering drone repositioning toward a high-risk sector or activating emergency acoustic "
          "dispersal sirens—remain strictly under human operator confirmation, preventing unintended autonomous panic triggers.")

    # 1.8 WORK BREAKDOWN AND INDIVIDUAL CONTRIBUTIONS
    add_section_heading(doc, "1.8", "Work Breakdown and Individual Contributions")
    add_p(doc,
          "In accordance with the collaborative research guidelines of course BCSE497J (Project I) at the School of Computer Science and "
          "Engineering, Vellore Institute of Technology, Chennai, the project was executed by a two-member team. The division of technical "
          "responsibilities between the team members is formally delineated below:")

    contrib_headers = ["Project Module & Engineering Domain", "Lead Technical Member", "Collaborating Member", "Key Delivered Subsystems"]
    contrib_rows = [
        ["Drone Hardware, Airframe & Propulsion", "Rohan Dubasi\n(23BRS1119)", "Tejas Ramesh Bodetti\n(23BRS1180)",
         "S500 airframe assembly, 2216 brushless motor installation, ESC calibration, power distribution board soldering, and balance testing."],

        ["Flight Controller Avionics & ArduPilot", "Rohan Dubasi\n(23BRS1119)", "Tejas Ramesh Bodetti\n(23BRS1180)",
         "Pixhawk 2.4.8 mounting, vibration dampening, IMU/compass calibration, FlySky FS-i6 RC binding, and failsafe RTL tuning."],

        ["Primary Payload & Dual-Adapter Network", "Tejas Ramesh Bodetti\n(23BRS1119)", "Rohan Dubasi\n(23BRS1180)",
         "GoPro Hero 13 mounting bracket, low-latency UDP pipeline (gopro_client.py), FFMPEG buffer bypass, and network routing separation."],

        ["ESP32 Crowd Speaker Hardware & Protocol", "Tejas Ramesh Bodetti\n(23BRS1180)", "Rohan Dubasi\n(23BRS1119)",
         "ESP32 DAC GPIO 25 audio amplifier circuit fabrication, GPIO 14 button interrupt, binary TCP audio server (esp32_manager.py), and TTS pipeline."],

        ["AI Detection & Multi-Object Tracking", "Tejas Ramesh Bodetti\n(23BRS1180)", "Rohan Dubasi\n(23BRS1119)",
         "YOLOv8 comparative evaluation, ByteTrack tracking integration, diagnosis and resolution of track ID churn (54 stable IDs vs. 100+ churn)."],

        ["Spatial Density & GPS Zone Localization", "Rohan Dubasi\n(23BRS1119)", "Tejas Ramesh Bodetti\n(23BRS1180)",
         "3×4 spatial grid zoning algorithm, per-zone density classification (Low/Med/High/Critical), pinhole camera ground-plane GPS projection."],

        ["Mission Control Web Dashboard & UI", "Tejas Ramesh Bodetti\n(23BRS1180)", "Rohan Dubasi\n(23BRS1119)",
         "Dark-themed responsive operations center dashboard (index.html), canvas zone overlay, real-time heatmap, trend chart, and demo video loop."],

        ["System Integration, Testing & Validation", "Joint Collaboration\n(Tejas & Rohan)", "Joint Collaboration\n(Tejas & Rohan)",
         "End-to-end integration testing, propulsion dynamometer measurements, hover endurance logging, video latency profiling, and thesis report."]
    ]
    add_table_data(doc, "1.2", "Formal Technical Responsibility Breakdown and Individual Deliverables", contrib_headers, contrib_rows,
                   col_widths=[1.5, 1.2, 1.2, 2.6])

    add_figure_placeholder(doc, "1.2",
                           "Project Work Breakdown and Execution Timeline",
                           "Gantt chart illustrating the 8 project development phases: Phase 1 (Literature review & requirement modeling), "
                           "Phase 2 (Drone hardware assembly & avionics setup), Phase 3 (Payload integration & dual-adapter networking), "
                           "Phase 4 (YOLOv8 implementation & ByteTrack integration), Phase 5 (Grid density estimation & GPS localization), "
                           "Phase 6 (ESP32 acoustic unit & TCP audio server), Phase 7 (Dashboard engineering & demo loop integration), "
                           "and Phase 8 (Experimental bench testing, latency profiling, and final documentation).")

    # 1.9 ORGANIZATION OF THE THESIS REPORT
    add_section_heading(doc, "1.9", "Organization of the Thesis Report")
    add_p(doc,
          "The remainder of this thesis report is methodically structured into eight comprehensive chapters, references, and appendices:\n\n"
          "• Chapter 2 (Literature Survey and Background): Conducts an exhaustive critical review of multi-rotor aerodynamics, UAV crowd surveillance "
          "systems, loudspeaker payload designs, video streaming protocols, ground-assisted computation paradigms, computer vision detectors, "
          "and spatial crowd density models, concluding with the identification of specific research gaps.\n\n"
          "• Chapter 3 (System Requirements and Mathematical Modelling of Drone Robotics & Payload): Presents the core mechanical and aerodynamic "
          "engineering of the drone platform. Derives momentum theory and Blade Element Momentum Theory (BEMT) equations; evaluates multi-rotor topologies "
          "and airframe designs; provides an exhaustive mass budget for the GoPro Hero 13 and ESP32 speaker payloads; sizes brushless motors and propellers; "
          "mathematically derives battery endurance and current draw; calculates 3D center of gravity shift and the moment of inertia tensor; and models "
          "anti-vibration damping transmissibility.\n\n"
          "• Chapter 4 (Ground-Assisted Architecture & Wireless Communication Infrastructure): Details the distributed system architecture, Pixhawk/ArduPilot "
          "avionics setup, the dual-adapter networking model separating video from telemetry, the low-latency UDP video ingestion pipeline (gopro_client.py), "
          "the binary TCP audio streaming protocol on port 8002 (esp32_manager.py), and asynchronous WebSocket synchronization.\n\n"
          "• Chapter 5 (Computer Vision, Density Estimation & Real-Time Alert Generation): Analyzes the object detection pipeline, comparing YOLOv8 variants "
          "(Nano to X-Large); details ByteTrack Kalman filtering and the empirical mitigation of track ID churn; establishes 3×4 grid density categorization; "
          "models pinhole camera ground-plane GPS projection; and formulates the multi-tier rule-based alert engine.\n\n"
          "• Chapter 6 (System Integration, Hardware Assembly & Mission Dashboard): Documents the step-by-step physical assembly of the drone airframe, "
          "vibration-isolated GoPro mounting, ESP32 speaker breadboard/PCB fabrication, ground station backend server architecture, and the full "
          "implementation of the mission control web dashboard featuring offline demo footage looping.\n\n"
          "• Chapter 7 (Experimental Results and Performance Evaluation): Analyzes empirical dynamometer thrust curves, hover endurance measurements, "
          "video transmission latency profiles, YOLOv8/ByteTrack detection and tracking metrics on test footage, acoustic sound pressure level (SPL) decay, "
          "and end-to-end emergency response times.\n\n"
          "• Chapter 8 (Conclusion and Future Work): Synthesizes the core technical contributions, summarizes critical engineering insights and operational "
          "limitations, and outlines a concrete roadmap for future research in autonomous repositioning and edge acceleration.\n\n"
          "• References & Appendices: Provides 35+ formal academic citations in APA format, followed by complete source code listings for the ESP32 firmware, "
          "ground-station server launch configurations, and motor dynamometer data sheets.")

    doc.add_page_break()
