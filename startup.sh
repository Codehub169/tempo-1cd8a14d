#!/bin/bash

echo "Starting the application setup..."

# Ensure the script exits on any error
set -e

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to the backend directory
echo "Setting up backend..."
cd "${SCRIPT_DIR}/backend"

# Create a Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "Python virtual environment created in backend/venv."
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  echo "WARNING: requirements.txt not found in backend. Skipping pip install."
fi
# Deactivate for now, will be reactivated to run the server
deactivate

echo "Backend setup complete."

# Navigate to the frontend directory
echo "Setting up frontend..."
cd "${SCRIPT_DIR}/frontend"

# Install frontend dependencies
if [ -f "package.json" ]; then
  npm install
else
  echo "ERROR: package.json not found in frontend. Cannot proceed."
  exit 1
fi

# Build the frontend application
echo "Building frontend application..."
npm run build
echo "Frontend build complete. Static files are in frontend/build."

# Navigate back to the backend directory to run the server from there
cd "${SCRIPT_DIR}/backend"

echo "Starting the application server..."

# Activate backend virtual environment again
source venv/bin/activate

# Run the FastAPI application using Uvicorn on port 9000
# The FastAPI app (app/main.py) will be configured to serve frontend static files from ../frontend/build
echo "Launching FastAPI server on http://localhost:9000"
echo "The backend API will be available, and it will serve the frontend."
# The --reload flag is for development. Remove for production if not desired.
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

echo "Application startup script finished."
