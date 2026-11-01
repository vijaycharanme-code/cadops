#!/usr/bin/env bash
set -e
echo "Starting CADMind Studio..."
python3 backend-sim/server.py 8000 &
SIM_PID=$!
cleanup() {
    kill $SIM_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM
cd frontend
npm run preview -- --port 1420 --host
