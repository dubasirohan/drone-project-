@echo off
echo ========================================================
<<<<<<< Updated upstream
echo   Starting Drone Crowd Monitoring System (DEMO MODE)
echo   Source: Sample Aerial Clip (test/clip.mp4)
echo ========================================================
echo.
echo 1. Starting Camera Handler on port 8081 (source: sample)...
start "Camera Handler (Demo)" cmd /k python src/gopro_client.py --port 8081 --source sample
timeout /t 3 /nobreak >nul
echo 2. Starting Analysis Server on port 8082...
start "Analysis Server" cmd /k python src/analysis_server.py --port 8082
echo.
echo ========================================================
echo   Dashboard available at: http://localhost:8082
echo   You can toggle between GoPro, Webcam, and Demo Footage
echo   directly from the dashboard at any time!
=======
echo   Drone Crowd Monitoring System - Live Demo Suite
echo   Includes: VisDrone UAV Scenarios ^& ESP32 Speaker
echo ========================================================
echo.
echo 1. Launching Camera Handler on port 8081...
start "Camera Handler" cmd /k python src/gopro_client.py --port 8081 --source sample
timeout /t 3 /nobreak >nul
echo 2. Launching AI Analysis ^& Dashboard Server on port 8082...
start "Analysis Server" cmd /k python src/analysis_server.py --port 8082
echo    Waiting for YOLOv8n + ByteTrack to initialize (approx 4 seconds)...
timeout /t 4 /nobreak >nul
echo.
echo 3. Opening Dashboard in your browser...
start http://localhost:8082
echo.
echo ========================================================
echo   Dashboard: http://localhost:8082
echo.
echo   Demo Features Available in Dashboard:
echo     * Sample Drone Video Clips:
echo         - Main Concourse: High Activity (37-45 People)
echo         - Clip 1: Aerial Corridor (11-15 People)
echo         - Clip 2: Urban Walkway (3-5 People)
echo         - Clip 3: Perimeter Patrol (2-4 People)
echo         - Clip 4: Transit Zone (1-2 People)
echo         - Clip 5: Overhead Survey
echo         - Clip 6: Broad Area Tactical Sweep
echo     * VisDrone Benchmark Scenarios:
echo         - S1: Park Walkway (Low Density)
echo         - S2: Urban Street (Low Density)
echo         - S3: Campus Concourse (Moderate Density)
echo         - S4: Shopping Plaza (High Density)
echo         - S5: Market Bottleneck (Critical Red Alert)
echo         - S6: Night Surveillance Square (Night UAV)
echo     * Live Overlays: YOLO Bounding Boxes ^& Zone Density Heatmap
echo     * Auto-Cycle Tour: Auto-transitions every 8 seconds
echo     * ESP32 Speaker Integration: Audio warnings ^& TTS
echo     * Live Hardware Feeds: GoPro Live ^& Webcam fallback
>>>>>>> Stashed changes
echo ========================================================
echo.
pause
