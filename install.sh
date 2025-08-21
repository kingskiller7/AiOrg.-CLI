#!/bin/bash

# This script installs all dependencies for both the backend and frontend.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Backend Installation ---
echo "Installing backend dependencies..."
cd backend
# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
# Activate virtual environment and install requirements
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# --- Frontend Installation ---
echo "Installing frontend dependencies..."
cd frontend
pnpm install
cd ..

echo "
Installation complete!"
echo "Please add your Gemini API key to backend/.env before starting the application."
