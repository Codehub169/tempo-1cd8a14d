from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from .routers import download

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TubeFetch & ReelGrab API",
    description="API for downloading YouTube videos/audio and Instagram Reels.",
    version="1.0.0"
)

# CORS Middleware
origins = [
    "http://localhost:3000",  # React development server ( Vite default port )
    "http://localhost:5173",  # React development server ( Create React App default port )
    "http://localhost:9000",  # Production port where backend serves frontend
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(download.router, prefix="/api")

# Serve Frontend Static Files
# Assumes the frontend is built into 'frontend/build' or 'frontend/dist'
project_root = Path(__file__).resolve().parent.parent.parent
frontend_build_path_options = [
    project_root / "frontend" / "build",
    project_root / "frontend" / "dist"
]

frontend_build_path = None
for path_option in frontend_build_path_options:
    if path_option.exists() and path_option.is_dir():
        frontend_build_path = path_option
        break

if frontend_build_path:
    logger.info(f"Serving frontend from: {frontend_build_path}")
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="static-frontend")
else:
    logger.warning(
        f"WARNING: Frontend build directory not found at expected locations: {frontend_build_path_options}. "
        f"Frontend will not be served by FastAPI. Ensure your frontend is built and the path is correct."
    )

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "API is running"}
