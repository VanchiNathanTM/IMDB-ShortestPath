#!/bin/bash

# Six Degrees of Movies - Stop Script for macOS/Linux
echo "[STOPPING] Shutting down all services..."

# Kill backend and frontend by port if they are running
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

docker compose down

echo "[OK] All services stopped."
