import yt_dlp
import asyncio
import os
import tempfile
import logging
from typing import Dict, Any, Tuple, Optional
import shutil

# Reusing helper from youtube_service to keep yt-dlp interaction logic centralized
from .youtube_service import _extract_yt_dlp_info, _format_filesize 

logger = logging.getLogger(__name__)

async def fetch_reel_info(url: str) -> Dict[str, Any]:
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
        'extract_flat': 'discard_in_playlist', # Handle if URL is part of a series/profile page
        'proxy': "" # Explicitly disable proxy
    }
    info = await _extract_yt_dlp_info(url, ydl_opts)

    full_description = info.get('description') or info.get('title')
    
    # Improved caption shortening to be more robust
    max_caption_length = 150 
    display_caption = full_description
    if full_description and len(full_description) > max_caption_length:
        # Try to break at a word boundary
        truncated = full_description[:max_caption_length]
        last_space = truncated.rfind(' ')
        if last_space != -1:
            display_caption = truncated[:last_space] + "..."
        else: # No space found, just truncate
            display_caption = truncated + "..."

    # Instagram often doesn't provide separate video/audio formats in the same way YouTube does
    # It usually gives direct URLs to the video file (often MP4).
    # We can still list it under a 'video_formats' like structure for consistency if needed by frontend,
    # or simplify if the frontend expects a direct download link.

    direct_video_url = None
    file_extension = info.get('ext', 'mp4') # Default to mp4 for reels
    file_size_bytes = info.get('filesize') or info.get('filesize_approx')

    # Check if 'url' key in info is the direct media URL
    if info.get('url') and info.get('protocol') in ['http', 'https', 'm3u8', 'rtmp']:
        direct_video_url = info.get('url')
    
    # Fallback: if formats list exists, try to find a suitable mp4 format
    elif info.get('formats'):
        for f in info['formats']:
            if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                direct_video_url = f.get('url')
                file_extension = f.get('ext', file_extension)
                file_size_bytes = f.get('filesize') or f.get('filesize_approx') or file_size_bytes
                break # Take the first suitable mp4 format

    return {
        'id': info.get('id'),
        'uploader': info.get('uploader'),
        'uploader_id': info.get('uploader_id'),
        'title': info.get('title') or full_description, 
        'description': full_description, 
        'caption': display_caption or "No caption available",
        'thumbnail': info.get('thumbnail'),
        'preview_image_url': info.get('thumbnail'), 
        'duration': info.get('duration'),
        'upload_date': info.get('upload_date'), 
        'original_url': info.get('webpage_url', url),
        'direct_video_url': direct_video_url, # This is the direct media URL from yt-dlp info
        'ext': file_extension, # Extension of the direct video
        'filesize_str': _format_filesize(file_size_bytes) if file_size_bytes else None
    }

async def download_reel(url: str, filename_prefix: str) -> Tuple[str, str, str]:
    temp_dir = tempfile.mkdtemp(prefix='reelgrab_')
    
    # Using a yt-dlp template that's less likely to cause issues with special characters
    # The client-provided `filename_prefix` will be used for Content-Disposition by the router.
    output_template = os.path.join(temp_dir, '%(uploader_id)s_%(id)s.%(ext)s')

    ydl_opts = {
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': False,
        # Prefer MP4, common for reels. yt-dlp will try to get the best single file.
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best',
        'extract_flat': 'discard_in_playlist',
        'proxy': "" # Explicitly disable proxy
    }

    try:
        # Perform the download
        info_dict = await _extract_yt_dlp_info(url, ydl_opts)
        
        downloaded_file_path = None
        if info_dict.get('requested_downloads') and len(info_dict['requested_downloads']) > 0:
            downloaded_file_path = info_dict['requested_downloads'][0].get('filepath')
        
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            logger.warning(f"'requested_downloads' not found or empty for Instagram reel {url}. Attempting to find file in temp_dir: {temp_dir}")
            files_in_temp = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            if not files_in_temp:
                raise FileNotFoundError(f"yt-dlp finished but no file was found in the temp directory for Reel: {temp_dir}. URL: {url}")
            downloaded_file_path = max(files_in_temp, key=lambda x: (os.path.getsize(x), os.path.getmtime(x)))
            logger.info(f"Fallback identified downloaded Reel file: {downloaded_file_path}")

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
             raise FileNotFoundError(f"Downloaded Reel file path could not be determined or does not exist: {downloaded_file_path} for URL: {url}")

        actual_filename_on_disk = os.path.basename(downloaded_file_path)
        logger.info(f"Instagram Reel downloaded to: {downloaded_file_path} (Disk filename: {actual_filename_on_disk}) for URL: {url}")
        
        return temp_dir, downloaded_file_path, actual_filename_on_disk

    except (ValueError, FileNotFoundError) as e: 
        logger.error(f"Error during Reel download for {url}: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True) 
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Reel download for {url}: {str(e)}", exc_info=True)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True) 
        raise ValueError(f"An unexpected error occurred during Reel download for {url}: {str(e)}")
