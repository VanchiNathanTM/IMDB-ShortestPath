@echo off
setlocal enabledelayedexpansion

REM Six Degrees of Movies - Startup Script
echo ====================================
echo Six Degrees of Movies - Starting...
echo ====================================
echo.

REM 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH.
    pause
    exit /b 1
)

REM 2. Check npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm not found in PATH.
    pause
    exit /b 1
)

REM 3. Check Docker
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Start Docker Desktop and try again.
    pause
    exit /b 1
)

REM 4. Install dependencies if needed
if not exist "frontend\node_modules\" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM 5. Find free ports
echo [CHECK] Finding available ports...
for /f "usebackq" %%i in (`python scripts\check_port.py 8001`) do set BACKEND_PORT=%%i
for /f "usebackq" %%i in (`python scripts\check_port.py 3000`) do set FRONTEND_PORT=%%i

if "!BACKEND_PORT!"=="" set BACKEND_PORT=8001
if "!FRONTEND_PORT!"=="" set FRONTEND_PORT=3000

echo [OK] Backend port: !BACKEND_PORT!
echo [OK] Frontend port: !FRONTEND_PORT!

REM 6. Start Neo4j
echo.
echo [STARTING] Neo4j database...
docker compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Neo4j via docker compose.
    pause
    exit /b 1
)

REM 7. Wait for Neo4j to be ready
echo [WAIT] Waiting for Neo4j to initialize...

set count=0
:wait_neo4j
set /a count+=1
if !count! gtr 60 (
    echo [ERROR] Neo4j failed to become ready.
    echo [HINT] Run: docker compose ps
    echo [HINT] Run: docker logs imdb_neo4j
    pause
    exit /b 1
)

REM Ensure container is running (not restarting/exited)
set NEO4J_STATUS=
for /f "usebackq delims=" %%s in (`docker inspect imdb_neo4j --format "{{.State.Status}}" 2^>nul`) do set NEO4J_STATUS=%%s
if /i not "!NEO4J_STATUS!"=="running" (
    timeout /t 1 /nobreak >nul
    goto wait_neo4j
)

REM Ensure Bolt is accepting cypher-shell connections
docker exec imdb_neo4j cypher-shell -u neo4j -p password "RETURN 1" >nul 2>&1
if !errorlevel! neq 0 (
    timeout /t 1 /nobreak >nul
    goto wait_neo4j
)

echo [OK] Neo4j is ready

REM 8. Start Backend
echo.
echo [STARTING] Backend API on port !BACKEND_PORT!...
start "IMDB-Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port !BACKEND_PORT! --reload"
timeout /t 2 /nobreak >nul

REM 9. Start Frontend
echo.
echo [STARTING] Frontend on port !FRONTEND_PORT!...
set PORT=!FRONTEND_PORT!
set REACT_APP_API_URL=http://localhost:!BACKEND_PORT!
start "IMDB-Frontend" cmd /k "cd frontend && set PORT=!FRONTEND_PORT! && set REACT_APP_API_URL=http://localhost:!BACKEND_PORT! && npm start"

echo.
echo ====================================
echo All services started!
echo ====================================
echo.
echo Neo4j Browser:  http://localhost:7474
echo Backend API:    http://localhost:!BACKEND_PORT!
echo Backend Docs:   http://localhost:!BACKEND_PORT!/docs
echo Frontend App:   http://localhost:!FRONTEND_PORT!
echo.
echo Press any key to STOP all services...
pause >nul

echo.
echo [STOPPING] Shutting down services...
taskkill /FI "WINDOWTITLE eq IMDB-Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq IMDB-Frontend*" /T /F >nul 2>&1
docker compose down

echo.
echo All services stopped.
