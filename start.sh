#!/bin/bash

# This script starts both the backend and frontend servers.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Start Backend Server ---
echo "Starting backend server on http://127.0.0.1:8000..."
cd backend
source venv/bin/activate
# Start Uvicorn in the background
uvicorn main:app --reload &
cd ..

# Give the backend a moment to start up
sleep 5

# --- Start Frontend Server ---
echo "Starting frontend server on http://localhost:3000..."
cd frontend
pnpm run dev
