@echo off
echo ========================================================
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
echo ========================================================
echo.
pause
