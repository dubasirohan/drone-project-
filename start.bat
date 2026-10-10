@echo off
echo Starting Drone Crowd Monitoring System...
echo.
echo Starting GoPro Handler on port 8081...
start "GoPro Handler" cmd /k python src/gopro_client.py --port 8081
timeout /t 3 /nobreak >nul
echo Starting Analysis Server on port 8082...
start "Analysis Server" cmd /k python src/analysis_server.py --port 8082
echo.
echo Dashboard will be available at http://localhost:8082
echo.
pause
