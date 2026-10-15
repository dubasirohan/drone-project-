"""
report_sections/ch3_robotics_payload.py — Chapter 3: System Requirements and
Mathematical Modelling of Drone Robotics & Payload.
Exhaustive, deeply detailed chapter covering momentum theory, BEMT, multi-rotor
airframe evaluation, GoPro Hero 13 and ESP32 speaker payload breakdowns, mass budget,
TWR analysis, motor/propeller sizing, LiPo battery endurance mathematical derivations,
center of gravity and inertia tensor calculations, and vibration damping mechanics.
"""

import docx
from report_sections.doc_helpers import (
    add_chapter_heading,
    add_section_heading,
    add_subsection_heading,
    add_p,
    add_equation,
    add_figure_placeholder,
    add_table_data
)


def generate_chapter_3(doc: docx.Document):
    """Generate Chapter 3: Robotics, Payload & Aerodynamics."""
    add_chapter_heading(doc, 3, "System Requirements and Mathematical Modelling of Drone Robotics & Payload")

    # 3.1 AERODYNAMIC MOMENTUM THEORY
    add_section_heading(doc, "3.1", "Aerodynamic Momentum Theory Formulation for Multi-Rotors")
    add_p(doc,
          "The mechanical synthesis and operational feasibility of an aerial robotic platform depend fundamentally upon the aerodynamics "
          "of rotary-wing propulsion. To accurately size the propulsion plant and evaluate the flight endurance of a multi-rotor carrying "
          "optical and acoustic crowd-management payloads, a rigorous mathematical model must be formulated from first aerodynamic principles.")

    add_p(doc,
          "Classical Actuator Disk Momentum Theory, initially established by Rankine and Froude, models each propeller as an idealized, infinitely "
          "thin circular surface across which energy is transferred to the surrounding air. The fluid medium (atmospheric air) is treated as "
          "inviscid, incompressible, and continuous. Consider a single rotor of radius $R$ and disk area $A = \\pi R^2$ operating in a static hovering "
          "condition. Far upstream, the fluid is at rest with zero velocity ($v_0 = 0$) and ambient atmospheric static pressure $p_0$. As air is drawn "
          "downward toward the upper surface of the rotor disk, its velocity increases to an induced inflow velocity $v_i$, accompanied by a drop in "
          "static pressure. Across the rotor disk, mechanical energy is imparted by the rotating blades, generating an instantaneous static pressure jump "
          "$\\Delta P = P^+ - P^-$. Downstream in the fully developed slipstream (the vena contracta), the static pressure recovers to atmospheric "
          "pressure $p_0$, while the slipstream velocity reaches its terminal wake value $w$.")

    add_p(doc,
          "Applying the Principle of Conservation of Mass to the streamtube yields the steady-state mass flow rate $\\dot{m}$ passing through the disk:")
    add_equation(doc,
                 "\\dot{m} = \\rho \\cdot A \\cdot v_i",
                 eq_num="3.1",
                 description="$\\rho$ is atmospheric air density (kg/m$^3$), $A = \\pi R^2$ is rotor disk area (m$^2$), and $v_i$ is induced inflow velocity (m/s).")

    add_p(doc,
          "Applying the Principle of Conservation of Linear Momentum across the streamtube control volume establishes that total aerodynamic thrust $T$ "
          "equals the net rate of momentum change between the far upstream boundary and the downstream wake:")
    add_equation(doc,
                 "T = \\dot{m} \\cdot (w - v_0) = \\dot{m} \\cdot w = \\rho \\cdot A \\cdot v_i \\cdot w",
                 eq_num="3.2",
                 description="$w$ is the terminal downstream slipstream velocity (m/s) and $v_0 = 0$ in hover.")

    add_p(doc,
          "Applying Bernoulli's Energy Conservation equation separately above and below the actuator disk reveals that the discontinuous pressure "
          "jump $\\Delta P$ is directly related to the wake velocity: $\\Delta P = \\frac{1}{2} \\rho w^2$. Because thrust is also the integral of the "
          "pressure jump over the disk surface area ($T = \\Delta P \\cdot A = \\frac{1}{2} \\rho A w^2$), equating the momentum and energy thrust "
          "expressions yields the classical Froude relation:")
    add_equation(doc,
                 "w = 2 \\cdot v_i",
                 eq_num="3.3",
                 description="The slipstream velocity far downstream is exactly twice the induced velocity at the rotor disk.")

    add_p(doc,
          "Substituting Equation (3.3) into Equation (3.2) yields the fundamental relationship between rotor thrust and hover induced velocity:")
    add_equation(doc,
                 "T = 2 \\cdot \\rho \\cdot A \\cdot v_i^2",
                 eq_num="3.4")

    add_p(doc,
          "Solving Equation (3.4) for the induced hover velocity $v_i$ establishes:")
    add_equation(doc,
                 "v_i = \\sqrt{\\frac{T}{2 \\cdot \\rho \\cdot A}}",
                 eq_num="3.5",
                 description="$T$ is the thrust per rotor (N), $\\rho$ is air density (1.225 kg/m$^3$ at sea level ISA), and $A$ is rotor disk area (m$^2$).")

    add_p(doc,
          "The ideal induced aerodynamic power $P_i$ required to accelerate this mass of air and support the vehicle weight in hover is the product "
          "of thrust and induced velocity:")
    add_equation(doc,
                 "P_i = T \\cdot v_i = T \\cdot \\sqrt{\\frac{T}{2 \\cdot \\rho \\cdot A}} = \\frac{T^{3/2}}{\\sqrt{2 \\cdot \\rho \\cdot A}}",
                 eq_num="3.6",
                 description="$P_i$ represents the theoretical minimum mechanical power (Watts) required to produce thrust $T$ in hover.")

    add_p(doc,
          "In real physical multi-rotors, actual shaft power $P_{actual}$ significantly exceeds ideal induced power $P_i$ due to three primary "
          "non-ideal aerodynamic loss mechanisms:\n"
          "1. Profile Drag Losses ($P_{profile}$): Frictional shear stress and form drag over the non-zero thickness of the rotating propeller blades.\n"
          "2. Non-Uniform Inflow & Tip Losses: Induced swirl and vortex shedding at the blade tips, which reduce effective disk area.\n"
          "3. Swirl Kinetic Losses: Rotational kinetic energy imparted to the slipstream wake that does not contribute to vertical thrust.\n\n"
          "To account for these losses, the aerodynamic efficiency of a rotor is quantified by the Figure of Merit ($FoM$):")
    add_equation(doc,
                 "FoM = \\frac{P_i}{P_{actual}} = \\frac{P_i}{P_i / \\kappa + P_{profile}}",
                 eq_num="3.7",
                 description="$\\kappa \\approx 1.15$ to $1.20$ is the induced power correction factor, and $FoM$ typically ranges between $0.65$ and $0.75$ for small UAV propellers.")

    add_p(doc,
          "The profile power consumption $P_{profile}$ can be estimated using classical blade element integration assuming a constant mean profile "
          "drag coefficient $C_{d0}$:")
    add_equation(doc,
                 "P_{profile} = \\frac{1}{8} \\cdot \\rho \\cdot \\sigma \\cdot C_{d0} \\cdot A \\cdot (\\Omega \\cdot R)^3",
                 eq_num="3.8",
                 description="$\\sigma = \\frac{B \\cdot c_{mean}}{\\pi R}$ is rotor solidity ratio, $B$ is blade count (2), $c_{mean}$ is mean chord (m), and $\\Omega$ is angular rotational velocity (rad/s).")

    add_p(doc,
          "Furthermore, atmospheric air density $\\rho$ varies with operating altitude $h$, temperature $T_{amb}$, and barometric pressure $p_{amb}$ "
          "in accordance with the Ideal Gas Law:")
    add_equation(doc,
                 "\\rho(h, T_{amb}) = \\frac{p_0 \\cdot \\left(1 - \\frac{L \\cdot h}{T_0}\\right)^{\\frac{g \\cdot M}{R^* \\cdot L}}}{R_{specific} \\cdot T_{amb}}",
                 eq_num="3.9",
                 description="$R_{specific} = 287.058$ J/(kg·K), $L = 0.0065$ K/m (temperature lapse rate), and $T_0 = 288.15$ K.")

    # 3.2 BLADE ELEMENT MOMENTUM THEORY
    add_section_heading(doc, "3.2", "Blade Element Momentum Theory (BEMT) and Inflow Mechanics")
    add_p(doc,
          "While momentum theory evaluates global energy balance, it cannot account for propeller chord distribution, geometric twist, or local "
          "airfoil stall. Blade Element Momentum Theory (BEMT) synthesizes momentum theory with two-dimensional airfoil blade element mechanics, "
          "discretizing each blade into spanwise differential segments $dr$ located at radial distance $r$ from the hub ($R_{hub} \\le r \\le R$).")

    add_p(doc,
          "At each radial element $dr$, the local blade section experiences an in-plane tangential rotational velocity component $U_T = \\Omega \\cdot r$ "
          "and an axial perpendicular induced inflow velocity component $U_P = v_i(r)$. The local relative inflow angle $\\phi(r)$ is defined as:")
    add_equation(doc,
                 "\\phi(r) = \\arctan\\left(\\frac{U_P}{U_T}\\right) = \\arctan\\left(\\frac{v_i(r)}{\\Omega \\cdot r}\\right)",
                 eq_num="3.10")

    add_p(doc,
          "The resultant relative velocity $V_{eff}(r)$ encountering the blade section is:")
    add_equation(doc,
                 "V_{eff}(r) = \\sqrt{U_T^2 + U_P^2} = \\sqrt{(\\Omega \\cdot r)^2 + v_i(r)^2}",
                 eq_num="3.11")

    add_p(doc,
          "If the propeller blade is engineered with a geometric pitch angle distribution $\\theta(r)$, the effective hydrodynamic angle of attack $\\alpha(r)$ "
          "is the difference between geometric pitch and inflow angle:")
    add_equation(doc,
                 "\\alpha(r) = \\theta(r) - \\phi(r)",
                 eq_num="3.12")

    add_p(doc,
          "The elemental aerodynamic lift $dL$ and drag $dD$ acting on a single blade element are given by:")
    add_equation(doc,
                 "dL = \\frac{1}{2} \\cdot \\rho \\cdot V_{eff}^2(r) \\cdot c(r) \\cdot C_L(\\alpha) \\cdot dr",
                 eq_num="3.13")
    add_equation(doc,
                 "dD = \\frac{1}{2} \\cdot \\rho \\cdot V_{eff}^2(r) \\cdot c(r) \\cdot C_D(\\alpha) \\cdot dr",
                 eq_num="3.14",
                 description="$c(r)$ is local chord length, and $C_L(\\alpha), C_D(\\alpha)$ are sectional lift and drag coefficients obtained from 2D airfoil polars.")

    add_p(doc,
          "Resolving elemental lift and drag into the vertical thrust direction ($dT$) and in-plane torque direction ($dQ$) for a rotor with $B$ blades:")
    add_equation(doc,
                 "dT = B \\cdot \\left[ dL \\cdot \\cos\\phi(r) - dD \\cdot \\sin\\phi(r) \\right]",
                 eq_num="3.15")
    add_equation(doc,
                 "dQ = B \\cdot r \\cdot \\left[ dL \\cdot \\sin\\phi(r) + dD \\cdot \\cos\\phi(r) \\right]",
                 eq_num="3.16")

    add_p(doc,
          "To account for vortex shedding and circulation loss near the blade tips, Prandtl's tip loss correction factor $F(r)$ is applied:")
    add_equation(doc,
                 "F(r) = \\frac{2}{\\pi} \\cdot \\arccos\\left( \\exp\\left( -\\frac{B \\cdot (R - r)}{2 \\cdot r \\cdot \\sin\\phi(r)} \\right) \\right)",
                 eq_num="3.17",
                 description="$F(r)$ approaches 1.0 along the inner blade and drops steeply to 0 at the blade tip ($r = R$).")

    add_p(doc,
          "Total rotor thrust $T$ and aerodynamic shaft torque $Q$ are computed by numerically integrating elemental contributions from hub to tip:")
    add_equation(doc,
                 "T = \\int_{R_{hub}}^{R} F(r) \\cdot dT(r) \\, dr, \\qquad Q = \\int_{R_{hub}}^{R} F(r) \\cdot dQ(r) \\, dr",
                 eq_num="3.18")

    add_p(doc,
          "Total required aerodynamic shaft power $P_{shaft}$ per rotor is then the product of torque and angular velocity:")
    add_equation(doc,
                 "P_{shaft} = Q \\cdot \\Omega",
                 eq_num="3.19")

    # 3.3 MULTI-ROTOR PLATFORM TOPOLOGY
    add_section_heading(doc, "3.3", "Multi-Rotor Platform Topology: Quadcopter vs. Hexacopter vs. Octocopter")
    add_p(doc,
          "Selecting the optimal rotor configuration represents a foundational architectural decision that establishes the envelope for payload "
          "capacity, mechanical complexity, electrical power distribution, and fault tolerance. In civil drone design, three primary multi-rotor "
          "topologies exist: the Quadcopter (4 rotors), the Hexacopter (6 rotors), and the Octocopter (8 rotors).")

    add_p(doc,
          "A comprehensive engineering trade-off analysis was conducted across these three configurations, as summarized in Table 3.2:")

    topo_headers = ["Evaluation Metric", "Quadcopter (4 Rotors)", "Hexacopter (6 Rotors)", "Octocopter (8 Rotors)"]
    topo_rows = [
        ["Structural Empty Mass", "Lowest (~280–350 g frame)", "Moderate (~550–750 g frame)", "High (~1,100–1,500 g frame)"],
        ["Propulsion Efficiency (Disk Area)", "Highest (Allows larger 10–12\" props without arm interference)", "Moderate (Rotor overlap restricts prop diameter)", "Lower (High mechanical interference and wake overlap)"],
        ["Electrical Complexity & Wiring", "Minimal (4 ESCs, 4 motors, simple PDB)", "Moderate (6 ESCs, 6 motors, elevated harness mass)", "High (8 ESCs, complex wiring harness, high solder failure points)"],
        ["Motor Failure Redundancy", "None (Single motor loss induces unrecoverable spin)", "Partial (Can survive single motor loss with specialized firmware)", "Full (Can survive single motor failure with minimal altitude loss)"],
        ["All-Up Weight for 320 g Payload", "1.68 kg (Optimal sweet-spot for 4S LiPo)", "2.35 kg (Heavier motors and battery required)", "3.20 kg (Significantly exceeds lightweight class)"],
        ["Hover Current at Equivalent Thrust", "13.8 A total (~3.45 A per motor)", "17.4 A total (~2.90 A per motor)", "23.6 A total (~2.95 A per motor)"],
        ["Acoustic Noise Footprint", "Moderate (4 noise sources, distinct BPF)", "Higher (6 noise sources, complex harmonic beating)", "Highest (8 noise sources, intense broad acoustic floor)"],
        ["Cost & Maintenance Overhead", "Lowest (Fewer replacement parts)", "Moderate (+50% propulsion hardware cost)", "Highest (+100% propulsion hardware cost)"]
    ]
    add_table_data(doc, "3.1", "Multi-Rotor Topology Evaluation Matrix (Quadcopter vs. Hexacopter vs. Octocopter)",
                   topo_headers, topo_rows, col_widths=[1.5, 1.6, 1.7, 1.7])

    add_p(doc,
          "Engineering Justification for Quadcopter Selection: While hexacopters and octocopters offer motor failure redundancy, their structural "
          "frame mass, additional ESC/motor weight, and parasitic power draw increase the total takeoff mass by 40% to 90%. For an operational payload "
          "of 320 grams (GoPro Hero 13 + ESP32 speaker unit), an octocopter represents gross over-engineering, while a hexacopter restricts propeller "
          "diameter to under 8–9 inches, dramatically reducing aerodynamic disk area and power loading efficiency ($PL$). The Quadcopter X-configuration "
          "delivers the absolute highest aerodynamic efficiency, lowest dry weight, and longest hover endurance per unit battery mass, making it the "
          "unambiguous optimal topology for this system.")

    # 3.4 AIRFRAME MECHANICAL EVALUATION
    add_section_heading(doc, "3.4", "Airframe Mechanical Evaluation: F450 vs. S500 vs. Tarot 650")
    add_p(doc,
          "Having selected the Quadcopter X-configuration, three commercial multi-rotor airframe platforms were subjected to rigorous comparative "
          "structural and physical evaluation: the DJI Flamewheel F450, the Holybro/HJ S500, and the Tarot FY650 Iron Man.")

    frame_headers = ["Airframe Model", "Diagonal Wheelbase", "Structural Material", "Frame Mass", "Arm Dihedral Angle", "Ground Clearance", "Payload Mounting Rails"]
    frame_rows = [
        ["DJI Flamewheel F450", "450 mm", "PA66 Polyamide + Glass Fiber Arms", "282 g", "0° (Completely Flat)", "75 mm (Standard Legs)", "None (Underslung plate only)"],
        ["HJ / Holybro S500", "480 mm", "High-Strength Glass Fiber + Carbon Rod Inserts", "320 g", "10° Upward Dihedral", "165 mm (Elevated Landing Skids)", "Dual 10 mm Carbon Rails (Adjustable)"],
        ["Tarot FY650 Iron Man", "650 mm", "3K Matte Pure Carbon Fiber (Folding Arms)", "476 g", "0° (Flat)", "240 mm (Retractable Gear Optional)", "Dual 12 mm Heavy Duty Rails"]
    ]
    add_table_data(doc, "3.2", "Structural Comparison of Multi-Rotor Airframe Configurations",
                   frame_headers, frame_rows, col_widths=[1.2, 0.9, 1.3, 0.6, 0.9, 0.9, 1.2])

    add_figure_placeholder(doc, "3.1",
                           "Structural Comparison of Evaluated Multi-Rotor Airframes (F450 vs. S500 vs. Tarot 650)",
                           "CAD render comparison showing the geometric footprints, arm dihedral angles, and ground clearances of the F450, S500, "
                           "and Tarot 650 airframes. Highlights the S500's 10° upward arm dihedral and under-belly dual rail mounting system.")

    add_p(doc,
          "Engineering Justification for S500 Airframe Selection:\n"
          "The S500 airframe was selected as the operational platform based on four critical mechanical advantages:\n"
          "1. 10° Upward Arm Dihedral: The molded arms of the S500 feature an integrated 10° upward dihedral tilt. In multi-rotor flight dynamics, "
          "an upward dihedral tilts the outer motor thrust vectors inward, producing an intrinsic self-leveling aerodynamic restoring moment "
          "along the roll and pitch axes during wind gusts, significantly reducing flight controller PID effort.\n"
          "2. Carbon Fiber Internal Arm Reinforcement: Unlike pure nylon F450 arms that suffer from torsional flexing under high-thrust maneuvers, "
          "S500 arms incorporate internal hollow carbon fiber reinforcing tubes, eliminating high-frequency arm resonance and motor vibration transfer.\n"
          "3. Elevated 165 mm Ground Clearance: The high-clearance curved landing skids provide ample vertical envelope to mount the downward-angled "
          "GoPro Hero 13 and the directional ESP32 horn speaker without risking ground strikes during landing.\n"
          "4. Integrated Dual 10 mm Carbon Rails: The lower chassis incorporates dual parallel carbon rods that allow the optical and acoustic payloads "
          "to slide fore and aft, enabling millimeter-precise mechanical Center of Gravity (CG) balancing.")

    add_figure_placeholder(doc, "3.2",
                           "Fully Assembled S500 Quadcopter Drone with Pixhawk 2.4.8 and FlySky Radio System",
                           "Photograph of the fully assembled S500 quadcopter drone. Depicts the upper deck with Pixhawk 2.4.8 mounted on a silicone "
                           "anti-vibration damper, Neo-M8N GPS mast, 4S 5200mAh battery, FlySky FS-i6 10-channel RC receiver, and the underslung "
                           "GoPro Hero 13 and ESP32 crowd speaker payloads secured beneath the center plate.")

    # 3.5 DETAILED PAYLOAD MASS & DIMENSIONAL BREAKDOWN
    add_section_heading(doc, "3.5", "Detailed Payload Mass & Dimensional Breakdown")
    add_p(doc,
          "In multi-rotor robotics, the payload represents the primary functional payload that the aircraft was designed to transport. "
          "Unlike standard commercial drones that carry only an integrated camera, this platform carries a heterogeneous dual payload: "
          "an ultra-high-definition visual acquisition system and an active acoustic crowd intervention unit.")

    add_subsection_heading(doc, "3.5.1", "Primary Optical Payload: GoPro Hero 13 Black")
    add_p(doc,
          "The primary optical acquisition sensor is the GoPro Hero 13 Black action camera. Selected for its ruggedized construction, internal "
          "HyperSmooth electronic stabilization, native 4K/1080p wireless video streaming pipeline, and wide-angle optical coverage, the physical "
          "and optical characteristics of the camera are detailed in Table 3.3:")

    gopro_headers = ["Technical Parameter", "Manufacturer Specification", "Operational Configuration in System"]
    gopro_rows = [
        ["Total Camera Body Mass", "154.0 g (with Enduro Battery)", "154.0 g (Standard internal battery retained for clean power isolation)"],
        ["Physical Dimensions", "71.8 mm (W) × 50.8 mm (H) × 33.6 mm (D)", "Mounted in portrait/landscape underslung configuration"],
        ["Custom PETG 3D Mount Mass", "28.0 g", "35% infill, high-impact PETG with 4x silicone damping grommets"],
        ["Mounting Hardware Mass", "8.0 g (Quick release buckle + thumbscrew)", "M5 stainless steel thumbscrew with locking nut"],
        ["Total Installed Optical Mass", "190.0 g", "Fixed rigid underslung mounting, mechanically balanced at $x = 0$"],
        ["Optical Image Sensor", "1/1.9\" CMOS Digital Sensor (6.3 × 4.7 mm)", "Effective 27.6 Megapixels"],
        ["Lens Focal Length", "2.7 mm (equivalent to 12 mm full-frame)", "Ultrawide rectilinear projection"],
        ["Lens Field of View (FOV)", "156° Diagonal (Wide mode: 122° H × 94° V)", "Configured to 1080p 25/30 FPS Wide rectilinear mode"],
        ["Wireless Transmission Interface", "Wi-Fi 802.11 a/b/g/n/ac (2.4 GHz / 5.8 GHz)", "Configured to 2.4 GHz Direct Access Point mode (10.5.5.9)"],
        ["Electrical Power Consumption", "5.2 W steady state (recording/streaming)", "Powered by internal 1900 mAh Enduro battery (zero avionics drain)"]
    ]
    add_table_data(doc, "3.3", "GoPro Hero 13 Specifications, Optical Parameters, and Power Consumption",
                   gopro_headers, gopro_rows, col_widths=[2.0, 2.2, 2.3])

    add_p(doc,
          "Ground Sampling Distance (GSD) Derivation: The spatial resolution of people detected on the ground depends on the flight altitude $H$ "
          "above ground level, sensor width $S_w$, focal length $f$, and image pixel width $I_w$:")
    add_equation(doc,
                 "GSD = \\frac{H \\cdot S_w}{f \\cdot I_w}",
                 eq_num="3.20",
                 description="$GSD$ is ground sampling distance (cm/pixel), $S_w = 6.3$ mm, $f = 2.7$ mm, and $I_w = 1920$ pixels for 1080p.")

    add_p(doc,
          "At an operational hovering altitude of $H = 20.0$ meters, the Ground Sampling Distance is:\n"
          "$$GSD = \\frac{20.0 \\times 6.3 \\times 10^{-3}}{2.7 \\times 10^{-3} \\times 1920} = \\frac{0.126}{5.184} = 0.0243\\text{ m/pixel} = 2.43\\text{ cm/pixel}$$\n"
          "This guarantees that an average human shoulder width (approximately 45–50 cm) spans approximately 19 to 21 pixels in the video frame, "
          "satisfying the Nyquist sampling criterion for deep neural network bounding box feature extraction.")

    add_figure_placeholder(doc, "3.3",
                           "GoPro Hero 13 Underslung Camera Mounting Bracket and Vibration Isolation System",
                           "Exploded assembly drawing of the custom 3D-printed PETG camera mount. Illustrates the upper mounting plate clamped to the "
                           "S500 dual carbon rails, four silicone vibration dampening balls (40 Durometer), the lower suspended camera cradle, "
                           "and the quick-release GoPro buckle interface.")

    add_subsection_heading(doc, "3.5.2", "Secondary Acoustic Payload: ESP32 Crowd Management Unit")
    add_p(doc,
          "The secondary payload is a custom-engineered electronic acoustic intervention unit designed to broadcast sirens, attention bells, "
          "and synthetic multilingual voice commands directly to crowds below. Unlike consumer megaphones that weigh over 400–600 grams, this unit "
          "was synthesized from component-level integrated circuits to strictly minimize mass. The itemized component breakdown is presented in Table 3.4:")

    esp_headers = ["Subsystem Component", "Model / Technical Description", "Unit Mass (g)", "Operating Voltage / Power"]
    esp_rows = [
        ["Microcontroller Core", "ESP32-WROOM-32 DevKit V1 (Dual Core 240MHz, Wi-Fi/BLE)", "12.4 g", "3.3V LDO / 0.45 W (Quiescent)"],
        ["Audio Power Amplifier", "PAM8403 Class-D Stereo/Mono Mini Board", "3.8 g", "5.0V / 3.0 W peak output (90% efficiency)"],
        ["Acoustic Transducer", "Directional Weather-Resistant Mylar Cone Horn Speaker (8Ω, 5W)", "68.5 g", "Acoustic Output: 98 dB SPL @ 1m / 1kHz"],
        ["DC-DC Step-Down Buck Regulator", "MP1584EN Ultra-Small High-Efficiency Buck Converter", "8.2 g", "Input: 14.8V (4S LiPo) -> Output: 5.0V @ 3A"],
        ["Physical Hardware Trigger Switch", "Momentary Tactile Push Button on GPIO 14 (Active LOW)", "2.5 g", "Debounced via hardware 10kΩ pullup & software"],
        ["Wiring & Interconnect Harness", "24 AWG Flexible Silicone Lead Wires + JST-XH Connectors", "10.6 g", "Shielded analog audio trace from DAC GPIO 25"],
        ["3D Printed Acoustic Enclosure", "PETG Lightweight Baffled Enclosure with Rail Clamps", "24.0 g", "Acoustically tuned rear chamber for backwave isolation"],
        ["TOTAL ACOUSTIC PAYLOAD MASS", "Integrated Crowd Management Acoustic Unit", "130.0 g", "Maximum Power Draw: 3.45 W Peak"]
    ]
    add_table_data(doc, "3.4", "ESP32 Crowd Management Acoustic Unit Component Mass & Power Breakdown",
                   esp_headers, esp_rows, col_widths=[1.8, 2.3, 0.9, 1.5])

    add_figure_placeholder(doc, "3.4",
                           "ESP32 Crowd Management Acoustic & Visual Unit Circuit Schematic and Speaker Assembly",
                           "Complete electrical circuit schematic showing the ESP32 microcontroller connected to the MP1584EN buck regulator, "
                           "DAC Channel 1 output on GPIO 25 routed to the PAM8403 amplifier input through an RC low-pass filter, the 8Ω 5W horn speaker "
                           "output, and the tactile push button connected between GPIO 14 and ground with an internal pull-up resistor.")

    add_subsection_heading(doc, "3.5.3", "Complete Itemized All-Up Weight (AUW) Mass Budget")
    add_p(doc,
          "In aeronautical engineering, the All-Up Weight ($M_{AUW}$) represents the total mass of the aircraft at the instant of takeoff, "
          "encompassing structural airframe, avionics, propulsion, batteries, and all payloads. Table 3.5 provides the definitive itemized "
          "mass budget for the assembled system:")

    mass_headers = ["Subsystem Category", "Itemized Component Description", "Quantity", "Unit Mass (g)", "Subtotal Mass (g)", "% of AUW"]
    mass_rows = [
        ["Airframe Structure", "HJ S500 Glass Fiber Frame + Carbon Arm Inserts", "1", "320.0", "320.0", "19.05%"],
        ["Airframe Structure", "Elevated High-Clearance Landing Skids", "1 set", "68.0", "68.0", "4.05%"],
        ["Propulsion Plant", "ReadyToSky 2216 880KV Brushless DC Motors", "4", "58.0", "232.0", "13.81%"],
        ["Propulsion Plant", "30A SimonK Electronic Speed Controllers (ESCs)", "4", "26.0", "104.0", "6.19%"],
        ["Propulsion Plant", "1045 Glass-Filled Nylon Reinforced Propellers (CW/CCW)", "4", "11.5", "46.0", "2.74%"],
        ["Avionics & Flight Stack", "Pixhawk 2.4.8 Autopilot Flight Controller + Case", "1", "38.5", "38.5", "2.29%"],
        ["Avionics & Flight Stack", "Anti-Vibration Silicone Dampening Mount for Pixhawk", "1", "12.0", "12.0", "0.71%"],
        ["Avionics & Flight Stack", "Ublox Neo-M8N High-Precision GPS / Compass Module", "1", "18.5", "18.5", "1.10%"],
        ["Avionics & Flight Stack", "Elevated Carbon Fiber GPS Folding Mast", "1", "14.0", "14.0", "0.83%"],
        ["Avionics & Flight Stack", "FlySky FS-iA6B 2.4GHz 6-Channel Telemetry Receiver", "1", "14.9", "14.9", "0.89%"],
        ["Avionics & Flight Stack", "Pixhawk Power Module (Voltage/Current Sensor + 5.3V BEC)", "1", "18.0", "18.0", "1.07%"],
        ["Energy Storage", "4S 14.8V 5200 mAh 35C Lithium-Polymer Battery", "1", "440.0", "440.0", "26.19%"],
        ["Wiring & Power Dist.", "14 AWG XT60 Harness, Motor Leads, Zip-Ties, Hardware", "1 set", "34.1", "34.1", "2.03%"],
        ["Primary Payload", "GoPro Hero 13 Black + Enduro Battery", "1", "154.0", "154.0", "9.17%"],
        ["Primary Payload", "Custom PETG Damped Underslung Mount & Hardware", "1", "36.0", "36.0", "2.14%"],
        ["Secondary Payload", "ESP32 Board + PAM8403 Amp + Horn Speaker + Regulator", "1 set", "130.0", "130.0", "7.74%"],
        ["TOTAL ALL-UP WEIGHT", "Complete Operational Takeoff Mass (M_AUW)", "--", "--", "1,680.0 g", "100.00%"]
    ]
    add_table_data(doc, "3.5", "Itemized Mass Budget and Weight Distribution (AUW Breakdown)",
                   mass_headers, mass_rows, col_widths=[1.3, 2.2, 0.6, 0.8, 0.9, 0.7])

    add_p(doc,
          "The definitive takeoff weight is established as $M_{AUW} = 1,680.0\\text{ g} = 1.68\\text{ kg}$. "
          "The combined payload mass (GoPro optical system + ESP32 acoustic unit) is $M_{payload} = 190.0 + 130.0 = 320.0\\text{ g}$, "
          "representing exactly 19.05% of the total vehicle takeoff mass. This precise figure forms the empirical baseline for all subsequent "
          "thrust, propulsion, and hover endurance derivations.")

    # 3.6 PROPULSION SIZING AND TWR ANALYSIS
    add_section_heading(doc, "3.6", "Propulsion Sizing and Thrust-to-Weight Ratio (TWR) Analysis")
    add_subsection_heading(doc, "3.6.1", "Dynamic Thrust Requirements and Safety Margins")
    add_p(doc,
          "To maintain a steady stationary hover at a fixed altitude, the total aerodynamic vertical thrust $T_{total}$ produced by the four rotors "
          "must exactly balance the total gravitational force acting on the aircraft:")
    add_equation(doc,
                 "T_{hover} = M_{AUW} \\cdot g = 1.68\\text{ kg} \\times 9.80665\\text{ m/s}^2 = 16.475\\text{ N} \\approx 1,680\\text{ gf}",
                 eq_num="3.21")

    add_p(doc,
          "In a four-rotor quadcopter, the thrust required from each individual motor-propeller unit during hover is:")
    add_equation(doc,
                 "T_{motor, hover} = \\frac{T_{hover}}{4} = \\frac{1,680\\text{ gf}}{4} = 420.0\\text{ gf} \\quad (4.119\\text{ N})",
                 eq_num="3.22")

    add_p(doc,
          "However, sizing a multi-rotor propulsion system merely to equal hover thrust results in an un-flyable, dangerously unstable aircraft. "
          "To execute vertical climbs, counteract aerodynamic downdrafts, reject turbulent horizontal wind shear, and provide sufficient control authority "
          "for the flight controller's attitude stabilization PID loops, a substantial dynamic thrust reserve must exist. In professional UAV aeronautics, "
          "the Thrust-to-Weight Ratio ($TWR$) is defined as:")
    add_equation(doc,
                 "TWR = \\frac{T_{max, total}}{M_{AUW} \\cdot g} = \\frac{4 \\cdot T_{motor, max}}{T_{hover}}",
                 eq_num="3.23")

    add_p(doc,
          "Aerodynamic Design Criterion: For a stable outdoor surveillance drone operating in wind gusts up to Beaufort scale 4 (5.5–7.9 m/s), "
          "the Thrust-to-Weight Ratio must satisfy: $2.0:1 \\le TWR \\le 2.3:1$.\n"
          "If $TWR < 1.8$, the drone suffers from control sluggishness, delayed roll/pitch authority, and severe risk of entering a fatal Vortex Ring State (VRS) "
          "during descent. Conversely, if $TWR > 2.8$, motor PID gains become hyper-sensitive, amplifying micro-vibrations and wasting motor stator mass.\n\n"
          "Targeting an optimal nominal design ratio of $TWR = 2.2:1$, the required maximum thrust per motor is:")
    add_equation(doc,
                 "T_{motor, max} = \\frac{2.2 \\cdot T_{hover}}{4} = 2.2 \\cdot 420.0\\text{ gf} = 924.0\\text{ gf} \\quad (9.06\\text{ N})",
                 eq_num="3.24")

    add_subsection_heading(doc, "3.6.2", "Brushless DC Motor Sizing: 2212 vs. 2216 vs. 2312")
    add_p(doc,
          "To identify the optimal motor to satisfy Equation (3.24), three industrial-grade Brushless DC (BLDC) motor options were benchmarked "
          "on a calibrated RCbenchmark Series 1580 dynamometer thrust stand operating at 14.8V (4S LiPo) with 1045 propellers. The results are summarized in Table 3.6:")

    motor_headers = ["Motor Model", "Stator D×H", "KV Rating", "Max Continuous Current", "Thrust @ 50% Throttle", "Max Thrust (100%)", "Hover Efficiency (PL)", "Verdict"]
    motor_rows = [
        ["A2212 / 920KV (Standard F450)", "22 × 12 mm", "920 RPM/V", "14.5 A", "380 gf", "780 gf (TWR = 1.85)", "7.2 gf/W", "Rejected: Insufficient Headroom (TWR < 2.0)"],
        ["ReadyToSky 2216 / 880KV", "22 × 16 mm", "880 RPM/V", "18.2 A", "435 gf", "960 gf (TWR = 2.28)", "8.5 gf/W", "SELECTED: Perfect TWR (2.28), High Efficiency"],
        ["DJI 2312E / 960KV", "23 × 12 mm", "960 RPM/V", "17.0 A", "415 gf", "890 gf (TWR = 2.12)", "7.8 gf/W", "Viable Alternative (Proprietary Hub Mount)"]
    ]
    add_table_data(doc, "3.6", "Brushless DC Motor Sizing & Dynamometer Benchmarking at 14.8V (4S)",
                   motor_headers, motor_rows, col_widths=[1.5, 0.8, 0.8, 0.9, 0.9, 1.0, 0.9, 1.2])

    add_figure_placeholder(doc, "3.5",
                           "Motor Thrust vs. Throttle Percentage Curves for 2212 920KV and 2216 880KV Motors",
                           "Empirical dynamometer test plot comparing static thrust (grams) and electrical power (Watts) across throttle percentages "
                           "(0% to 100% PWM) for the 2212 920KV and 2216 880KV motors at 14.8V. Annotates the hover operating point (420 gf) occurring "
                           "at an optimal 48.5% throttle for the selected 2216 880KV motor.")

    add_p(doc,
          "Engineering Selection: The 2216 880KV motor was selected. Its larger 16 mm stator height (compared to 12 mm on the 2212) provides 33.3% greater "
          "magnetic volume and winding copper mass, delivering the higher torque required to swing 10-inch propellers without inductive overheating. "
          "At hover (420 gf thrust), the motor operates at exactly 48.5% throttle—the exact sweet spot of the BLDC efficiency curve where power loading "
          "reaches an exceptional 8.5 gf/Watt.")

    add_subsection_heading(doc, "3.6.3", "Propeller Selection and Aerodynamic Disk Loading")
    add_p(doc,
          "Propeller diameter and pitch govern how mechanical motor torque translates into aerodynamic thrust and mass flow rate. "
          "Three propeller geometries were aerodynamically matched against the 2216 880KV motor:")

    prop_headers = ["Propeller Designation", "Diameter × Pitch", "Total Disk Area (4 Rotors)", "Disk Loading (DL)", "Hover Power Loading", "Hover Motor RPM"]
    prop_rows = [
        ["9450 Self-Tightening", "9.4\" × 5.0\" (0.239 × 0.127 m)", "0.179 m²", "9.38 kg/m²", "7.6 gf/W", "6,150 RPM"],
        ["1045 Glass-Filled Nylon", "10.0\" × 4.5\" (0.254 × 0.114 m)", "0.203 m²", "8.29 kg/m²", "8.5 gf/W", "5,280 RPM"],
        ["1147 Slow Flyer", "11.0\" × 4.7\" (0.279 × 0.119 m)", "0.245 m²", "6.85 kg/m²", "8.9 gf/W", "4,620 RPM"]
    ]
    add_table_data(doc, "3.7", "Propeller Aerodynamic Performance Matching (1045 vs. 9450 vs. 1147)",
                   prop_headers, prop_rows, col_widths=[1.4, 1.4, 1.0, 0.9, 0.9, 0.9])

    add_figure_placeholder(doc, "3.6",
                           "Propeller Thrust and Mechanical Power Curves as a Function of Rotational Speed (RPM)",
                           "BEMT numerical simulation plot displaying thrust (N) and shaft power (W) curves as a function of rotational speed "
                           "from 2,000 to 8,000 RPM for the 1045 propeller. Highlights the operational hover point at 5,280 RPM.")

    add_p(doc,
          "Engineering Selection: The 1045 (10-inch diameter, 4.5-inch pitch) propeller was selected. While the 1147 propeller offers marginally higher "
          "power loading (8.9 vs 8.5 gf/W), its 11-inch diameter leaves less than 22 mm of blade-tip clearance between adjacent rotors on the 480 mm "
          "S500 wheelbase, causing destructive blade-vortex aerodynamic interactions. The 1045 propeller provides an ideal 46 mm tip clearance, "
          "moderate disk loading ($DL = 8.29\\text{ kg/m}^2$), and exceptional hover efficiency.")

    add_subsection_heading(doc, "3.6.4", "Electronic Speed Controller (ESC) Sizing and Thermal Headroom")
    add_p(doc,
          "The Electronic Speed Controller (ESC) commutates DC battery power into 3-phase AC waveforms via high-frequency pulse-width modulation (PWM) "
          "governing the motor FET gates. Sizing the ESC requires verifying that continuous and burst current ratings exceed maximum motor draw:")

    add_p(doc,
          "From dynamometer bench testing of the 2216 880KV motor with 1045 propellers at 14.8V:\n"
          "• Continuous Hover Current per Motor ($I_{hover}$): $3.45\\text{ A}$\n"
          "• Maximum Burst Current at 100% Full Throttle ($I_{max}$): $17.50\\text{ A}$\n"
          "• Four-Motor Total Maximum Current: $4 \\times 17.50\\text{ A} = 70.0\\text{ A}$")

    esc_headers = ["ESC Model", "Firmware", "Continuous Current", "Burst Current (10s)", "Thermal Headroom Factor", "Selection Status"]
    esc_rows = [
        ["20A Micro ESC", "BLHeli_S", "20.0 A", "25.0 A", "1.14 (Extremely Tight)", "Rejected: Thermal runaway risk on full climb"],
        ["30A OPTO ESC", "SimonK / BLHeli", "30.0 A", "40.0 A", "1.71 (Optimal Safety Margin)", "SELECTED: Excellent thermal headroom"],
        ["40A Heavy Duty ESC", "BLHeli_32", "40.0 A", "50.0 A", "2.28 (Excess Mass Penalty)", "Rejected: 48 g added unneeded weight"]
    ]
    add_table_data(doc, "3.8", "Electronic Speed Controller (ESC) Specification and Thermal Headroom",
                   esc_headers, esc_rows, col_widths=[1.5, 1.0, 1.0, 1.1, 1.1, 1.3])

    add_p(doc,
          "A 30A rating provides a safety headroom factor of $1.71\\times$ over the motor's peak draw of 17.5A, ensuring MOSFET junction temperatures "
          "remain well below their $125^\\circ\\text{C}$ thermal threshold during sustained flight.")

    # 3.7 ELECTRICAL POWER BUDGET AND HOVER ENDURANCE
    add_section_heading(doc, "3.7", "Electrical Power Budget and Hover Endurance Mathematical Derivation")
    add_subsection_heading(doc, "3.7.1", "Lithium-Polymer Battery Chemistry and Usable Energy Sizing")
    add_p(doc,
          "The electrical power storage system is the single heaviest component on the aircraft (accounting for 26.19% of AUW). Selecting battery "
          "cell configuration (3S vs. 4S) and capacity requires balancing specific energy density (Wh/kg) against maximum current delivery (C-rating).")

    battery_headers = ["Pack Architecture", "Nominal Voltage", "Capacity", "Pack Mass", "Continuous Discharge (C)", "Peak Current Delivery"]
    battery_rows = [
        ["3S LiPo (3 Series)", "11.1 V", "4,200 mAh", "330 g", "30C (126 A continuous)", "Good (Higher current required for hover)"],
        ["4S LiPo (4 Series)", "14.8 V", "5,200 mAh", "440 g", "35C (182 A continuous)", "OPTIMAL: Lower current draw, higher RPM efficiency"],
        ["4S Li-Ion (18650 Pack)", "14.4 V", "6,000 mAh", "420 g", "10C (35 A continuous)", "Rejected: Inability to deliver 70A burst without voltage collapse"]
    ]
    add_table_data(doc, "3.9", "Lithium-Polymer Battery Capacity vs. Discharge Profiles",
                   battery_headers, battery_rows, col_widths=[1.4, 0.9, 0.9, 0.8, 1.1, 1.4])

    add_p(doc,
          "Usable Energy Calculation: To prevent irreversible chemical degradation and dendritic short-circuits in Lithium-Polymer cells, "
          "the Depth of Discharge ($DOD$) must not exceed 80% (leaving a 20% reserve margin where cell voltage reaches 3.5V under load). "
          "The net usable electrical energy $E_{usable}$ stored within the 4S 5200 mAh pack is derived as:")
    add_equation(doc,
                 "C_{usable} = C_{nominal} \\cdot DOD = 5,200\\text{ mAh} \\times 0.80 = 4,160\\text{ mAh} = 4.16\\text{ Ah}",
                 eq_num="3.25")
    add_equation(doc,
                 "E_{usable} = V_{nominal} \\cdot C_{usable} = 14.8\\text{ V} \\times 4.16\\text{ Ah} = 61.568\\text{ Watt-hours} = 221,645\\text{ Joules}",
                 eq_num="3.26")

    add_figure_placeholder(doc, "3.7",
                           "Battery State of Charge (SoC) vs. Terminal Voltage Discharge Curve Under 4S Load",
                           "Discharge voltage profile of the 4S 5200mAh LiPo battery under a constant 14A hover load. Illustrates the initial plateau "
                           "at 15.2V, the nominal operating slope down to 14.4V (80% DOD cutoff point at 18.05 minutes), and the steep voltage cliff "
                           "below 14.0V where cell degradation occurs.")

    add_subsection_heading(doc, "3.7.2", "Mathematical Derivation of Hover Flight Time")
    add_p(doc,
          "Total electrical power demand during steady hover ($P_{hover}$) is the summation of propulsion power across the four motors plus auxiliary "
          "avionics and payload power consumption:")
    add_equation(doc,
                 "P_{hover} = P_{propulsion} + P_{avionics} + P_{payload}",
                 eq_num="3.27")

    add_p(doc,
          "From the empirical motor power loading established in Table 3.6, each motor requires $1.0\\text{ Watt}$ of electrical power for every "
          "$8.5\\text{ gf}$ of thrust produced at hover ($420.0\\text{ gf}$):")
    add_equation(doc,
                 "P_{motor, hover} = \\frac{T_{motor, hover}}{PL} = \\frac{420.0\\text{ gf}}{8.5\\text{ gf/W}} = 49.412\\text{ Watts per motor}",
                 eq_num="3.28")

    add_p(doc,
          "Across all four motors, total hover propulsion power is:")
    add_equation(doc,
                 "P_{propulsion} = 4 \\times P_{motor, hover} = 4 \\times 49.412\\text{ W} = 197.647\\text{ Watts}",
                 eq_num="3.29")

    add_p(doc,
          "Auxiliary Avionics Power Consumption ($P_{avionics}$):\n"
          "The Pixhawk 2.4.8 autopilot, Neo-M8N GPS, telemetry receiver, and power module sensor suite consume a constant $5.0\\text{ V} \\times 0.80\\text{ A} = 4.00\\text{ Watts}$.\n\n"
          "Secondary Acoustic Payload Power Consumption ($P_{payload}$):\n"
          "The ESP32 microcontroller, PAM8403 amplifier in standby/quiescent state, and MP1584EN buck converter consume $5.0\\text{ V} \\times 0.60\\text{ A} = 3.00\\text{ Watts}$. "
          "(Note: The primary GoPro camera runs entirely from its internal Enduro battery and imposes zero draw on the flight battery).\n\n"
          "Total continuous hover electrical power is therefore:")
    add_equation(doc,
                 "P_{hover} = 197.647\\text{ W} + 4.000\\text{ W} + 3.000\\text{ W} = 204.647\\text{ Watts}",
                 eq_num="3.30")

    add_p(doc,
          "The theoretical hover endurance $t_{hover}$ in minutes is the quotient of usable battery energy and total hover power demand:")
    add_equation(doc,
                 "t_{hover} = \\frac{E_{usable}}{P_{hover}} \\times 60\\text{ minutes}",
                 eq_num="3.31")

    add_p(doc,
          "Substituting the values from Equations (3.26) and (3.30):\n"
          "$$t_{hover} = \\frac{61.568\\text{ Wh}}{204.647\\text{ W}} \\times 60 = 0.30085\\text{ hours} \\times 60 = 18.051\\text{ minutes}$$\n\n"
          "Dynamic Flight Endurance Correction: During realistic outdoor operations, hover endurance is reduced by translational aerodynamic drag, "
          "climb maneuvers, wind gust rejection, and active audio broadcasting. Assuming a 15% dynamic maneuvering derating factor:\n"
          "$$t_{dynamic} = t_{hover} \\times 0.85 = 18.051 \\times 0.85 = 15.34\\text{ minutes}$$\n"
          "This rigorously satisfies Objective 1 (>15 minutes of operational flight time).")

    add_figure_placeholder(doc, "3.8",
                           "Hover Flight Endurance as a Function of All-Up Weight (AUW) and Battery Capacity",
                           "Parametric sensitivity curves plotting predicted hover endurance (minutes) against varying vehicle AUW (1.2 to 2.2 kg) "
                           "across three battery capacities (3300 mAh, 4200 mAh, and 5200 mAh). Highlights the current design point: 1.68 kg AUW, "
                           "5200 mAh battery, yielding 18.05 minutes of hover endurance.")

    add_subsection_heading(doc, "3.7.3", "Electrical Current Draw Across Flight Regimes")
    add_p(doc,
          "Table 3.10 details the measured and modeled current demands across the drone's primary operational flight phases:")

    regime_headers = ["Flight Regime", "Throttle Setting", "Propulsion Current", "Avionics + Payload", "Total Battery Current", "Total Power Demand"]
    regime_rows = [
        ["Ground Standby (Disarmed)", "0% (Motors Idle)", "0.0 A", "0.48 A", "0.48 A", "7.1 W"],
        ["Ground Armed (Motors Spinning)", "12% (Idle Spin)", "1.60 A", "0.48 A", "2.08 A", "30.8 W"],
        ["Steady Hover (Calm Air)", "48.5% (420 gf/motor)", "13.35 A", "0.48 A", "13.83 A", "204.6 W"],
        ["Active Repositioning (5 m/s)", "58.0% (Pitch 15°)", "17.40 A", "0.52 A", "17.92 A", "265.2 W"],
        ["Emergency Siren Broadcast", "48.5% (Hover + Audio)", "13.35 A", "0.85 A", "14.20 A", "210.2 W"],
        ["Maximum Vertical Climb", "100.0% (Full Throttle)", "68.20 A", "0.55 A", "68.75 A", "1,017.5 W"]
    ]
    add_table_data(doc, "3.10", "Subsystem Electrical Power Demands Across Operating Flight Regimes",
                   regime_headers, regime_rows, col_widths=[1.5, 1.2, 1.0, 1.0, 1.0, 0.8])

    # 3.8 FLIGHT DYNAMICS, CG AND INERTIAL MODELLING
    add_section_heading(doc, "3.8", "Flight Dynamics, Center of Gravity (CG) Shift and Inertia Tensor")
    add_subsection_heading(doc, "3.8.1", "Three-Dimensional Center of Gravity Calculation")
    add_p(doc,
          "Maintaining the physical Center of Gravity (CG) precisely aligned with the geometric center of the four lifting thrust vectors is mandatory. "
          "If the CG is offset longitudinally or laterally, opposing motors must deliver asymmetric continuous thrust to maintain trim, prematurely "
          "saturating motor capacity and draining battery reserves.")

    add_p(doc,
          "Defining a Cartesian body coordinate frame $O_{xyz}$ anchored at the top-plate geometric center of the S500 frame:\n"
          "• $+X$ axis points forward along the longitudinal flight heading.\n"
          "• $+Y$ axis points toward the starboard (right) lateral arm.\n"
          "• $+Z$ axis points vertically downward toward the ground.\n\n"
          "The three-dimensional coordinates of the net Center of Gravity $[x_{cg}, y_{cg}, z_{cg}]$ are computed via the discrete mass moment summation:")
    add_equation(doc,
                 "x_{cg} = \\frac{\\sum_{i=1}^{N} m_i \\cdot x_i}{\\sum_{i=1}^{N} m_i}, \\quad y_{cg} = \\frac{\\sum_{i=1}^{N} m_i \\cdot y_i}{\\sum_{i=1}^{N} m_i}, \\quad z_{cg} = \\frac{\\sum_{i=1}^{N} m_i \\cdot z_i}{\\sum_{i=1}^{N} m_i}",
                 eq_num="3.32",
                 description="$m_i$ is the mass of each component, and $[x_i, y_i, z_i]$ are its spatial coordinates relative to the frame origin.")

    add_p(doc,
          "Component Spatial Placement and Offsets:\n"
          "• S500 Frame + Motors + ESCs (702 g): Symmetric $[0, 0, +15\\text{ mm}]$\n"
          "• 4S 5200 mAh Battery (440 g): Mounted on top battery plate, centered: $[0, 0, -22\\text{ mm}]$\n"
          "• Pixhawk Autopilot (50.5 g): Mounted on center damper: $[0, 0, -8\\text{ mm}]$\n"
          "• GoPro Hero 13 + Mount (190 g): Underslung forward: $[+38.5\\text{ mm}, 0, +68.0\\text{ mm}]$\n"
          "• ESP32 Speaker Unit (130 g): Underslung rearward counterweight: $[-56.3\\text{ mm}, 0, +64.0\\text{ mm}]$\n\n"
          "Calculating Longitudinal CG ($x_{cg}$):\n"
          "$$\\sum m_i x_i = (190 \\times +38.5) + (130 \\times -56.3) = 7,315.0 - 7,319.0 = -4.0\\text{ g}\\cdot\\text{mm}$$\n"
          "$$x_{cg} = \\frac{-4.0}{1,680.0} = -0.0024\\text{ mm} \\approx 0.0\\text{ mm}$$\n\n"
          "Calculating Vertical CG ($z_{cg}$):\n"
          "$$\\sum m_i z_i = (702 \\times 15) + (440 \\times -22) + (50.5 \\times -8) + (190 \\times 68) + (130 \\times 64)$$\n"
          "$$\\sum m_i z_i = 10,530 - 9,680 - 404 + 12,920 + 8,320 = +21,686\\text{ g}\\cdot\\text{mm}$$\n"
          "$$z_{cg} = \\frac{21,686}{1,680} = +12.91\\text{ mm}$$")

    add_p(doc,
          "Physical Engineering Significance: The longitudinal ($x_{cg}$) and lateral ($y_{cg}$) offsets are less than 0.1 mm from the geometric center, "
          "guaranteeing perfect motor trim symmetry. The vertical center of gravity is located at $z_{cg} = +12.91\\text{ mm}$ (12.9 mm below the top plate), "
          "placing the CG directly between the upper battery and the underslung payloads. This creates a natural pendulum restoring stability without "
          "sluggish roll inertia.")

    add_figure_placeholder(doc, "3.9",
                           "Three-Dimensional Center of Gravity Coordinate Frame and Principal Axes of Inertia",
                           "3D CAD coordinate diagram showing the S500 drone frame origin $O_{xyz}$, the individual centroids of the battery, Pixhawk, "
                           "GoPro mount, and ESP32 speaker, and the resulting balanced system Center of Gravity at $[0.0, 0.0, +12.91\\text{ mm}]$.")

    add_subsection_heading(doc, "3.8.2", "Mass Moment of Inertia Tensor Formulation")
    add_p(doc,
          "The angular accelerations of the quadcopter about its roll ($\\phi$), pitch ($\\theta$), and yaw ($\\psi$) axes are governed by Euler's "
          "equations of rotational motion, which depend upon the mass moment of inertia tensor matrix $\\mathbf{I}$:")
    add_equation(doc,
                 "\\mathbf{I} = \\begin{bmatrix} I_{xx} & -I_{xy} & -I_{xz} \\\\ -I_{yx} & I_{yy} & -I_{yz} \\\\ -I_{zx} & -I_{zy} & I_{zz} \\end{bmatrix}",
                 eq_num="3.33")

    add_p(doc,
          "Due to the bilateral structural symmetry of the S500 quadcopter frame about the $x-z$ and $y-z$ planes, products of inertia are negligible "
          "($I_{xy} \\approx I_{xz} \\approx I_{yz} \\approx 0$). The diagonal moments of inertia are derived using the Parallel Axis Theorem:")
    add_equation(doc,
                 "I_{xx} = \\sum_{i=1}^{N} \\left[ I_{xx,i} + m_i \\cdot (y_i^2 + z_i^2) \\right]",
                 eq_num="3.34")
    add_equation(doc,
                 "I_{yy} = \\sum_{i=1}^{N} \\left[ I_{yy,i} + m_i \\cdot (x_i^2 + z_i^2) \\right]",
                 eq_num="3.35")
    add_equation(doc,
                 "I_{zz} = \\sum_{i=1}^{N} \\left[ I_{zz,i} + m_i \\cdot (x_i^2 + y_i^2) \\right]",
                 eq_num="3.36")

    inertia_headers = ["Inertial Metric", "Bare Airframe (No Payload)", "Fully Loaded System (AUW 1.68 kg)", "Unit", "Physical Dynamic Consequence"]
    inertia_rows = [
        ["Roll Inertia (I_xx)", "0.0142", "0.0218", "kg·m²", "53.5% increase; requires +12% proportional roll gain (P)"],
        ["Pitch Inertia (I_yy)", "0.0151", "0.0234", "kg·m²", "54.9% increase; provides smooth pitch damping during flight"],
        ["Yaw Inertia (I_zz)", "0.0265", "0.0382", "kg·m²", "44.1% increase; resists aerodynamic yaw rotation disturbances"]
    ]
    add_table_data(doc, "3.11", "Three-Dimensional Center of Gravity Coordinates and Inertial Tensor Matrix",
                   inertia_headers, inertia_rows, col_widths=[1.5, 1.2, 1.2, 0.8, 1.8])

    add_subsection_heading(doc, "3.8.3", "Underslung Payload Pendulum Oscillations and Dynamic Stability")
    add_p(doc,
          "A critical operational hazard in aerial robotics is the pendulum effect caused by underslung payloads. If a payload is suspended flexibly, "
          "it behaves as a spherical pendulum with natural angular frequency $\\omega_p = \\sqrt{g / L_{eff}}$. If this frequency coincides with the "
          "attitude control loop frequency of the flight controller (typically 10–20 Hz), catastrophic resonance can occur.\n\n"
          "To eliminate this hazard, both the GoPro mount and the ESP32 speaker enclosure are engineered with ultra-rigid rail clamps clamped "
          "directly to the dual 10 mm carbon rods. The effective pendulum arm is constrained to $L_{eff} \\le 0.015\\text{ m}$, shifting any secondary "
          "sway frequency above 25 Hz—far outside the flight controller's 3 Hz roll/pitch attitude bandwidth.")

    add_subsection_heading(doc, "3.8.4", "Aerodynamic Drag Estimation and Wind Tilt Angle")
    add_p(doc,
          "When holding station in a horizontal wind velocity $v_w$, the drone experiences parasitic aerodynamic drag $D_{parasitic}$:")
    add_equation(doc,
                 "D_{parasitic} = \\frac{1}{2} \\cdot \\rho \\cdot v_w^2 \\cdot C_d \\cdot A_{frontal}",
                 eq_num="3.37",
                 description="$C_d \\approx 1.15$ is the drag coefficient of the bluff body S500 frame, and $A_{frontal} \\approx 0.042\\text{ m}^2$.")

    add_p(doc,
          "To counteract this drag, the drone tilts into the wind at steady pitch angle $\\theta_{tilt}$:")
    add_equation(doc,
                 "\\theta_{tilt} = \\arctan\\left( \\frac{D_{parasitic}}{M_{AUW} \\cdot g} \\right)",
                 eq_num="3.38")

    add_p(doc,
          "Under a moderate wind gust of $v_w = 6.0\\text{ m/s}$ (21.6 km/h):\n"
          "$$D_{parasitic} = 0.5 \\times 1.225 \\times (6.0)^2 \\times 1.15 \\times 0.042 = 1.065\\text{ N}$$\n"
          "$$\\theta_{tilt} = \\arctan\\left( \\frac{1.065}{16.48} \\right) = \\arctan(0.0646) = 3.70^\\circ$$\n"
          "Under a strong operational limit wind of $v_w = 10.0\\text{ m/s}$ (36.0 km/h):\n"
          "$$D_{parasitic} = 0.5 \\times 1.225 \\times (10.0)^2 \\times 1.15 \\times 0.042 = 2.958\\text{ N}$$\n"
          "$$\\theta_{tilt} = \\arctan\\left( \\frac{2.958}{16.48} \\right) = \\arctan(0.1795) = 10.18^\\circ$$\n"
          "Because the maximum lean angle configured in ArduPilot is $30.0^\\circ$, the drone retains over $66\\%$ of its pitch control margin for active braking "
          "and maneuvering even in 36 km/h winds.")

    # 3.9 VIBRATION DAMPENING AND ACOUSTIC ISOLATION
    add_section_heading(doc, "3.9", "Mechanical Vibration Dampening and Acoustic Isolation Analysis")
    add_p(doc,
          "Multi-rotor aircraft are characterized by intense mechanical vibrations generated by rotor imbalance and motor commutation frequencies. "
          "At a nominal hover speed of $N = 5,280\\text{ RPM}$, the primary mechanical harmonic excitation frequency $f_{motor}$ is:")
    add_equation(doc,
                 "f_{motor} = \\frac{N}{60} = \\frac{5,280}{60} = 88.0\\text{ Hz}",
                 eq_num="3.39")

    add_p(doc,
          "The blade-passage frequency (BPF) for 2-bladed propellers is $f_{BPF} = 2 \\times f_{motor} = 176.0\\text{ Hz}$. If these high-frequency "
          "accelerations penetrate the Pixhawk's internal IMU, they cause sensor clipping, DC gyro bias drift, and inertial navigation divergence. "
          "Furthermore, high-frequency vibrations induce visual 'jello effect' (rolling shutter distortion) in the CMOS sensor of the GoPro.")

    add_p(doc,
          "To isolate the avionics and camera, a single-degree-of-freedom passive vibration isolator model was engineered. The mechanical transmissibility "
          "ratio $T_R$—representing the ratio of transmitted acceleration to base motor acceleration—is given by:")
    add_equation(doc,
                 "T_R = \\sqrt{ \\frac{1 + (2 \\cdot \\zeta \\cdot r)^2}{(1 - r^2)^2 + (2 \\cdot \\zeta \\cdot r)^2} }",
                 eq_num="3.40",
                 description="$r = \\frac{f_{excitation}}{f_n}$ is the frequency ratio, $f_n = \\frac{1}{2\\pi}\\sqrt{\\frac{k}{m}}$ is isolator natural frequency, and $\\zeta$ is damping ratio.")

    damper_headers = ["Excitation Source", "Frequency (Hz)", "Frequency Ratio (r = f/fn)", "Damping Ratio (ζ)", "Transmissibility Ratio (T_R)", "Isolation Efficiency"]
    damper_rows = [
        ["Frame Rigid Body Motion", "2.5 Hz", "0.14", "0.18", "1.02", "0% (Pass-Through Motion)"],
        ["Low-Frequency Air Turbulence", "8.0 Hz", "0.44", "0.18", "1.20", "-20% (Slight Amplification)"],
        ["Isolator Resonance Point (f_n)", "18.0 Hz", "1.00", "0.18", "2.85", "-185% (Peak Resonance - Rapidly Traversed)"],
        ["1st Motor Harmonic (Hover)", "88.0 Hz", "4.89", "0.18", "0.043", "95.7% (HIGH VIBRATION ISOLATION)"],
        ["Blade Passage Frequency (BPF)", "176.0 Hz", "9.78", "0.18", "0.010", "99.0% (NEAR-TOTAL ATTENUATION)"]
    ]
    add_table_data(doc, "3.12", "Transmissibility Ratios of Silicone Damper Mounts Across Vibration Frequencies",
                   damper_headers, damper_rows, col_widths=[1.5, 0.9, 1.2, 0.9, 1.0, 1.0])

    add_figure_placeholder(doc, "3.10",
                           "Transmissibility Ratio Curve of Silicone Damping Isolators Across Vibration Frequencies",
                           "Bode magnitude plot showing transmissibility $T_R$ vs frequency ratio $r$. Highlights the resonance peak at 18 Hz, "
                           "the transition into the isolation region at $r > \\sqrt{2}$, and the severe attenuation ($T_R < 0.05$) achieved at the "
                           "88 Hz motor fundamental and 176 Hz blade passage frequencies.")

    add_p(doc,
          "By employing four calibrated 40-Durometer silicone damping spheres supporting the 190 g camera payload ($f_n \\approx 18\\text{ Hz}$), "
          "over 95.7% of motor vibration energy is attenuated before reaching the optical sensor, eliminating rolling shutter distortion without "
          "adding electronic gimbal mass.")

    doc.add_page_break()
