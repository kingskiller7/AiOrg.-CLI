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

# Give the backend a moment to start up
sleep 5

# --- Start Frontend Server ---
echo "Starting frontend server on http://localhost:3000..."
cd frontend
pnpm run dev
