from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import os
import logging
import shutil
from typing import Optional

from ..services import youtube_service, instagram_service
from ..models import YouTubeVideoInfo, InstagramReelInfo

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/youtube/info", tags=["YouTube"], response_model=YouTubeVideoInfo)
async def get_youtube_info_route(url: str = Query(..., description="The YouTube video URL")):
    """Fetches information and available formats for a YouTube video."""
    try:
        logger.info(f"Fetching YouTube info for URL: {url}")
        info = await youtube_service.fetch_video_info(url)
        if not info or not info.get('id'):
            raise HTTPException(status_code=404, detail="Video information not found or could not be processed.")
        return info
    except ValueError as ve:
        logger.error(f"Validation error fetching YouTube info for {url}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching YouTube info for {url}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.get("/youtube/download", tags=["YouTube"])
async def download_youtube_media_route(
    url: str = Query(..., description="The YouTube video URL"), 
    format_id: str = Query(..., description="The format ID to download"), 
    media_type: str = Query(..., alias="type", description="The type of media ('video' or 'audio')"), 
    filename: str = Query(..., description="Desired filename for the download")
):
    """Downloads YouTube video or audio for a given format ID."""
    temp_dir = None
    try:
        logger.info(f"YouTube download request: URL={url}, FormatID={format_id}, Type={media_type}, Filename={filename}")
        temp_dir, file_path, _ = await youtube_service.download_media(url, format_id, media_type, filename)
        
        return FileResponse(
            path=file_path,
            filename=filename, 
            media_type='application/octet-stream',
            background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True)
        )
    except ValueError as ve:
        logger.error(f"Validation error downloading YouTube media for {url}, format {format_id}: {str(ve)}")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fnfe:
        logger.error(f"File not found during YouTube download for {url}, format {format_id}: {str(fnfe)}")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=404, detail="Downloaded file could not be found on server.")
    except Exception as e:
        logger.error(f"Error downloading YouTube media for {url}, format {format_id}: {str(e)}", exc_info=True)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up temp directory {temp_dir} due to error.")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred during download: {str(e)}")

@router.get("/instagram/info", tags=["Instagram"], response_model=InstagramReelInfo)
async def get_instagram_info_route(url: str = Query(..., description="The Instagram Reel URL")):
    """Fetches information about an Instagram Reel."""
    try:
        logger.info(f"Fetching Instagram info for URL: {url}")
        info = await instagram_service.fetch_reel_info(url)
        if not info or not info.get('id'):
            raise HTTPException(status_code=404, detail="Reel information not found or could not be processed.")
        return info
    except ValueError as ve:
        logger.error(f"Validation error fetching Instagram info for {url}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching Instagram info for {url}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.get("/instagram/download", tags=["Instagram"])
async def download_instagram_reel_route(
    url: str = Query(..., description="The Instagram Reel URL"), 
    filename: Optional[str] = Query(None, description="Desired filename for the download. Defaults if not provided.")
):
    """Downloads an Instagram Reel."""
    temp_dir = None
    DEFAULT_INSTAGRAM_FILENAME = "instagram_reel_default.mp4"
    effective_filename: str

    if filename and filename.strip():
        effective_filename = filename.strip()
        # Basic check for potentially problematic characters. This is not exhaustive.
        # The primary goal is to provide a reasonable filename for the Content-Disposition header.
        # Avoid characters like / \ and null bytes. Others might be relevant depending on OS.
        if '/' in effective_filename or '\\' in effective_filename or '\0' in effective_filename:
            logger.warning(f"Provided filename '{effective_filename}' contains problematic characters. Using default.")
            effective_filename = DEFAULT_INSTAGRAM_FILENAME
    else:
        effective_filename = DEFAULT_INSTAGRAM_FILENAME
        logger.warning(f"Filename not provided or invalid for Instagram Reel download (URL: {url}). Using default: {effective_filename}")
        
    try:
        logger.info(f"Instagram Reel download request: URL={url}, Effective Filename={effective_filename}")
        temp_dir, file_path, _ = await instagram_service.download_reel(url, effective_filename)
        
        return FileResponse(
            path=file_path, 
            filename=effective_filename, 
            media_type='video/mp4',
            background=BackgroundTask(shutil.rmtree, temp_dir, ignore_errors=True)
        )
    except ValueError as ve:
        logger.error(f"Validation error downloading Instagram Reel for {url}: {str(ve)}")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fnfe:
        logger.error(f"File not found during Instagram Reel download for {url}: {str(fnfe)}")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=404, detail="Downloaded file could not be found on server.")
    except Exception as e:
        logger.error(f"Error downloading Instagram Reel for {url}: {str(e)}", exc_info=True)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up temp directory {temp_dir} due to error.")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred during download: {str(e)}")
