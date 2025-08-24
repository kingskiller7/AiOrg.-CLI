#!/bin/bash

# This script starts both the backend and frontend servers.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Start Backend Server ---
echo "Starting backend server on http://127.0.0.1:8000..."
# Activate the virtual environment from the root
source backend/venv/bin/activate
# Set PYTHONPATH to include the backend directory and run uvicorn
PYTHONPATH=backend uvicorn backend.main:app --reload &

# --- Wait for Backend Server ---
echo "Waiting for backend server to be ready..."
while ! curl -s http://127.0.0.1:8000 > /dev/null; do
    sleep 1
done
echo "Backend server is ready."

# --- Start Frontend Server ---
echo "Starting frontend server on http://localhost:3000..."
cd frontend
pnpm run dev

# Deactivate the virtual environment when the script is interrupted
# This will be triggered by Ctrl+C
trap "deactivate; kill 0" INT TERM
# Wait for all background processes to finish
wait