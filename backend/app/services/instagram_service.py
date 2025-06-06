import yt_dlp
import asyncio
import os
import tempfile
import logging
from typing import Dict, Any, Tuple, Optional
import shutil

from .youtube_service import _extract_yt_dlp_info # Reusing helper from youtube_service

logger = logging.getLogger(__name__)

async def fetch_reel_info(url: str) -> Dict[str, Any]:
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
    }
    info = await _extract_yt_dlp_info(url, ydl_opts)

    full_description = info.get('description') or info.get('title')
    
    max_caption_length = 150 
    display_caption = full_description
    if full_description and len(full_description) > max_caption_length:
        display_caption = full_description[:max_caption_length].rsplit(' ', 1)[0] + "..." 

    return {
        'id': info.get('id'),
        'uploader': info.get('uploader'),
        'uploader_id': info.get('uploader_id'),
        'title': info.get('title') or full_description, # Full title or description
        'description': full_description, # Full description from yt-dlp
        'caption': display_caption or "No caption available", # Shortened for display
        'thumbnail': info.get('thumbnail'),
        'preview_image_url': info.get('thumbnail'), # Alias for frontend consistency
        'duration': info.get('duration'),
        'upload_date': info.get('upload_date'), # YYYYMMDD
        'original_url': info.get('webpage_url', url), # Correctly mapped originalUrl
        'direct_video_url': info.get('url') if info.get('ext') == 'mp4' else None,
    }

async def download_reel(url: str, filename_prefix: str) -> Tuple[str, str, str]:
    temp_dir = tempfile.mkdtemp(prefix='reelgrab_')
    
    output_template = os.path.join(temp_dir, '%(uploader)s_%(id)s.%(ext)s') # More specific naming

    ydl_opts = {
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': False,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Prefer MP4
    }

    try:
        info_dict = await _extract_yt_dlp_info(url, ydl_opts)
        
        downloaded_file_path = None
        if info_dict.get('requested_downloads') and len(info_dict['requested_downloads']) > 0:
            downloaded_file_path = info_dict['requested_downloads'][0].get('filepath')
        
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            logger.warning("'requested_downloads' not found or empty for Instagram, attempting to find file in temp_dir")
            files_in_temp = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            if not files_in_temp:
                raise FileNotFoundError(f"yt-dlp finished but no file was found in the temp directory for Reel: {temp_dir}")
            downloaded_file_path = max(files_in_temp, key=os.path.getmtime)
            logger.info(f"Fallback found downloaded Reel file: {downloaded_file_path}")

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
             raise FileNotFoundError(f"Downloaded Reel file path could not be determined or does not exist: {downloaded_file_path}")

        actual_filename_on_disk = os.path.basename(downloaded_file_path)
        logger.info(f"Instagram Reel downloaded to: {downloaded_file_path} (Disk filename: {actual_filename_on_disk})")
        
        return temp_dir, downloaded_file_path, actual_filename_on_disk

    except (ValueError, FileNotFoundError) as e: 
        logger.error(f"Error during Reel download preparation for {url}: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True) 
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Reel download for {url}: {str(e)}", exc_info=True)
        shutil.rmtree(temp_dir, ignore_errors=True) 
        raise ValueError(f"An unexpected error occurred during Reel download: {str(e)}")
