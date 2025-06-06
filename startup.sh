#!/bin/bash

# Ensure the script exits on any error FIRST
set -e

# Unset common proxy environment variables at the beginning
unset HTTP_PROXY HTTPS_PROXY FTP_PROXY SOCKS_PROXY ALL_PROXY NO_PROXY
unset http_proxy https_proxy ftp_proxy socks_proxy all_proxy no_proxy

# Add explicit logging of their state AFTER unsetting
echo "Checking proxy variables after attempting to unset them in startup.sh:"
echo "HTTP_PROXY='${HTTP_PROXY:-not set}'"
echo "HTTPS_PROXY='${HTTPS_PROXY:-not set}'"
echo "FTP_PROXY='${FTP_PROXY:-not set}'"
echo "SOCKS_PROXY='${SOCKS_PROXY:-not set}'"
echo "ALL_PROXY='${ALL_PROXY:-not set}'"
echo "NO_PROXY='${NO_PROXY:-not set}'"
echo "http_proxy='${http_proxy:-not set}'"
echo "https_proxy='${https_proxy:-not set}'"
echo "ftp_proxy='${ftp_proxy:-not set}'"
echo "socks_proxy='${socks_proxy:-not set}'"
echo "all_proxy='${all_proxy:-not set}'"
echo "no_proxy='${no_proxy:-not set}'"

echo "Starting the application setup..."

# Check for core dependencies
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 could not be found. Please install Python 3."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "ERROR: npm could not be found. Please install Node.js and npm."
    exit 1
fi

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Backend Setup
echo "Setting up backend..."
cd "${SCRIPT_DIR}/backend"

VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating Python virtual environment in backend/${VENV_DIR}..."
  python3 -m venv "$VENV_DIR"
  echo "Python virtual environment created."
fi

# Activate virtual environment
# shellcheck source=venv/bin/activate
source "${VENV_DIR}/bin/activate"

if [ -f "requirements.txt" ]; then
  echo "Installing/updating pip in virtual environment..."
  if ! python -m pip install --upgrade pip; then
    echo "WARNING: Failed to upgrade pip. Continuing with current version."
  fi
  echo "Installing backend dependencies from requirements.txt..."
  if ! pip install --no-cache-dir -r requirements.txt; then
    echo "ERROR: pip install failed in backend directory. Please check pip logs."
    deactivate
    exit 1
  fi
  echo "Backend dependencies installed successfully."
else
  echo "WARNING: requirements.txt not found in backend. Skipping pip install."
fi

# Deactivate for now; will be reactivated to run the server
deactivate
echo "Backend setup complete."

# Frontend Setup
echo "Setting up frontend..."
cd "${SCRIPT_DIR}/frontend"

if [ -f "package.json" ]; then
  echo "Installing frontend dependencies from package.json..."
  if ! npm install; then
    echo "ERROR: npm install failed in frontend directory. Please check npm logs."
    exit 1
  fi
  echo "Frontend dependencies installed successfully."
  
  echo "Building frontend application..."
  if ! npm run build; then
    echo "ERROR: npm run build failed. Please check build logs."
    exit 1
  fi
  echo "Frontend build complete. Static files are likely in frontend/build or frontend/dist."
else
  echo "ERROR: package.json not found in frontend. Cannot proceed with frontend setup."
  exit 1
fi

# Navigate back to the backend directory to run the server
cd "${SCRIPT_DIR}/backend"

echo "Starting the application server..."

# Activate backend virtual environment again
# shellcheck source=venv/bin/activate
source "${VENV_DIR}/bin/activate"

# Run the FastAPI application using Uvicorn
echo "Launching FastAPI server on http://0.0.0.0:9000"
echo "The backend API will be available, and it will serve the frontend."
# The --reload flag is for development. Remove or set based on an environment variable for production.
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

echo "Application startup script finished."
