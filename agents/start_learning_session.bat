@echo off
echo ========================================
echo AUTONOMOUS LEARNING SESSION
echo Professor Agent + Alpha Agent
echo Duration: 5 minutes
echo ========================================
echo.

cd /d "%~dp0"

echo Building Docker containers...
docker-compose -f docker-compose.agents.yml build

echo.
echo Starting learning session...
docker-compose -f docker-compose.agents.yml up

echo.
echo Session complete. Check logs in volumes.
pause
