#!/bin/bash

# Six Degrees of Movies - Startup Script for macOS/Linux
echo "===================================="
echo "Six Degrees of Movies - Starting..."
echo "===================================="
echo

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found in PATH."
    exit 1
fi

# 2. Check npm
if ! command -v npm &> /dev/null; then
    echo "[ERROR] npm not found in PATH."
    exit 1
fi

# 3. Check Docker
if ! docker info &> /dev/null; then
    echo "[ERROR] Docker is not running. Start Docker Desktop and try again."
    exit 1
fi

# 4. Install dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

# 5. Find free ports
echo "[CHECK] Finding available ports..."
BACKEND_PORT=$(python3 scripts/check_port.py 8001)
FRONTEND_PORT=$(python3 scripts/check_port.py 3000)

echo "[OK] Backend port: $BACKEND_PORT"
echo "[OK] Frontend port: $FRONTEND_PORT"

# 6. Start Neo4j
echo
echo "[STARTING] Neo4j database..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to start Neo4j via docker compose."
    exit 1
fi

# 7. Wait for Neo4j to be ready
echo "[WAIT] Waiting for Neo4j to initialize..."
count=0
while true; do
    count=$((count + 1))
    if [ $count -gt 60 ]; then
        echo "[ERROR] Neo4j failed to become ready."
        exit 1
    fi

    NEO4J_STATUS=$(docker inspect imdb_neo4j --format "{{.State.Status}}" 2>/dev/null)
    if [ "$NEO4J_STATUS" == "running" ]; then
        if docker exec imdb_neo4j cypher-shell -u neo4j -p password "RETURN 1" &> /dev/null; then
            break
        fi
    fi
    sleep 1
done

echo "[OK] Neo4j is ready"

# 8. Start Backend
echo
echo "[STARTING] Backend API on port $BACKEND_PORT..."
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
BACKEND_PID=$!
cd ..

# 9. Start Frontend
echo
echo "[STARTING] Frontend on port $FRONTEND_PORT..."
export PORT=$FRONTEND_PORT
export REACT_APP_API_URL=http://localhost:$BACKEND_PORT
cd frontend && npm start &
FRONTEND_PID=$!
cd ..

echo
echo "===================================="
echo "All services started!"
echo "===================================="
echo
echo "Neo4j Browser:  http://localhost:7474"
echo "Backend API:    http://localhost:$BACKEND_PORT"
echo "Backend Docs:   http://localhost:$BACKEND_PORT/docs"
echo "Frontend App:   http://localhost:$FRONTEND_PORT"
echo
echo "Press Ctrl+C to STOP all services..."

# Handle shutdown
cleanup() {
    echo
    echo "[STOPPING] Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    docker compose down
    exit
}

trap cleanup SIGINT

# Wait for background processes
wait
