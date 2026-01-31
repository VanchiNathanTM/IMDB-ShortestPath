@echo off
REM Stop all Six Degrees of Movies services

echo [STOPPING] Shutting down all services...

taskkill /FI "WINDOWTITLE eq IMDB-Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq IMDB-Frontend*" /T /F >nul 2>&1

REM Kill by port as fallback
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

docker compose down

echo [OK] All services stopped.
