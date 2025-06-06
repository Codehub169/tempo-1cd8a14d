import yt_dlp
import asyncio
import os
import tempfile
import logging
from typing import Dict, Any, Tuple, Callable, List
import shutil # For robust directory cleanup

logger = logging.getLogger(__name__)

class BackgroundTask:
    """A simple background task wrapper for file/directory cleanup."""
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_dir_task = kwargs.pop('is_dir', False)

    async def __call__(self):
        try:
            if self.is_dir_task:
                logger.info(f"Attempting to remove directory: {self.args[0]}")
                shutil.rmtree(*self.args, **self.kwargs) # Use shutil.rmtree for directories
            else:
                logger.info(f"Attempting to remove file: {self.args[0]}")
                os.remove(*self.args, **self.kwargs)
            logger.info(f"Successfully executed background cleanup: {self.func.__name__} on {self.args[0]}")
        except Exception as e:
            logger.error(f"Error in background cleanup task {self.func.__name__} on {self.args[0]}: {str(e)}")

async def _extract_yt_dlp_info(url: str, ydl_opts: Dict) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=ydl_opts.get('skip_download', True) is False))
            return info
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp DownloadError processing {url}: {str(e)}")
        # Customize error messages for common issues
        if "Unsupported URL" in str(e):
            raise ValueError(f"The provided URL is not supported: {url}")
        if "Video unavailable" in str(e):
            raise ValueError("This video is unavailable.")
        if "Private video" in str(e):
            raise ValueError("This video is private.")
        if "Login required" in str(e).lower() or "authentication required" in str(e).lower():
             raise ValueError("This content requires login or authentication, which is not supported.")
        raise ValueError(f"Could not process URL ({url}): {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error with yt-dlp for {url}: {str(e)}", exc_info=True)
        raise ValueError(f"An unexpected error occurred while processing URL ({url}): {str(e)}")

async def fetch_video_info(url: str) -> Dict[str, Any]:
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
        'youtube_include_dash_manifest': False, # Avoids overly verbose DASH formats
    }
    info = await _extract_yt_dlp_info(url, ydl_opts)

    video_formats: List[Dict[str, Any]] = []
    audio_formats: List[Dict[str, Any]] = []

    if info.get('formats'):
        for f in info['formats']:
            # Video formats (with audio, common containers)
            if (f.get('vcodec') != 'none' and f.get('acodec') != 'none' and 
                f.get('ext') in ['mp4', 'webm'] and f.get('filesize')):
                video_formats.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'resolution': f.get('resolution') or f'{f.get("width")}x{f.get("height")}' or f.get('format_note'),
                    'filesize': f.get('filesize'),
                    'fps': f.get('fps'),
                    'note': f.get('format_note', '') + (f' (vcodec: {f.get("vcodec")}, acodec: {f.get("acodec")})' if f.get('vcodec') and f.get('acodec') else '')
                })
            # Audio-only formats (common containers)
            elif (f.get('acodec') != 'none' and f.get('vcodec') == 'none' and 
                  f.get('ext') in ['m4a', 'mp3', 'opus', 'ogg', 'wav'] and f.get('filesize')):
                audio_formats.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'filesize': f.get('filesize'),
                    'abr': f.get('abr'),
                    'note': f.get('format_note', '') + (f' (acodec: {f.get("acodec")})' if f.get("acodec") else '')
                })
    
    # Sort by filesize (approx) descending, could also sort by resolution/bitrate
    video_formats.sort(key=lambda x: x.get('filesize') or 0, reverse=True)
    audio_formats.sort(key=lambda x: (x.get('abr') or 0, x.get('filesize') or 0), reverse=True)

    return {
        'id': info.get('id'),
        'title': info.get('title', 'N/A'),
        'thumbnail': info.get('thumbnail'),
        'duration': info.get('duration'),
        'duration_string': info.get('duration_string'),
        'channel': info.get('uploader') or info.get('channel'),
        'view_count': info.get('view_count'),
        'upload_date': info.get('upload_date'), # YYYYMMDD format
        'video_formats': video_formats,
        'audio_formats': audio_formats
    }

async def download_media(url: str, format_id: str, media_type: str, filename_prefix: str) -> Tuple[str, str]:
    temp_dir = tempfile.mkdtemp(prefix='tubefetch_')
    
    # yt-dlp will determine the extension. filename_prefix is for the browser suggestion.
    # The actual filename on disk will be based on title and actual extension.
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': False, # Ensure download happens
        # 'verbose': True, # For debugging download issues
    }

    # No specific audio postprocessing here; rely on format_id selection.
    # If format_id is a video format, yt-dlp downloads it. If it's an audio-only format, it downloads that.
    # The frontend is expected to choose an appropriate format_id (e.g., an audio-only one for audio downloads).

    try:
        info_dict = await _extract_yt_dlp_info(url, ydl_opts)
        
        downloaded_file_path = None
        # yt-dlp >= 2023.06.22 populates 'requested_downloads'
        if info_dict.get('requested_downloads') and len(info_dict['requested_downloads']) > 0:
            downloaded_file_path = info_dict['requested_downloads'][0].get('filepath')
        
        # Fallback if 'requested_downloads' is not available or empty (older yt-dlp or edge cases)
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            # If outtmpl was a fixed name (not using templates), this would be simpler.
            # With templates, we must find the file. Assume it's the only/newest in temp_dir.
            logger.warning("'requested_downloads' not found or empty, attempting to find file in temp_dir")
            files_in_temp = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            if not files_in_temp:
                raise FileNotFoundError(f"yt-dlp finished but no file was found in the temp directory: {temp_dir}")
            downloaded_file_path = max(files_in_temp, key=os.path.getctime) # Get the newest file
            logger.info(f"Fallback found downloaded file: {downloaded_file_path}")

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
             raise FileNotFoundError(f"Downloaded file path could not be determined or does not exist: {downloaded_file_path}")

        actual_filename_on_disk = os.path.basename(downloaded_file_path)
        logger.info(f"Media downloaded to: {downloaded_file_path} (Disk filename: {actual_filename_on_disk})")
        
        # Return the full path to the file and its name on disk.
        # The router will use the 'filename_prefix' for the browser's suggested download name.
        return downloaded_file_path, actual_filename_on_disk

    except (ValueError, FileNotFoundError) as e: # Catch our own specific errors or FileNotFoundError
        logger.error(f"Error during media download preparation for {url}, format {format_id}: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True) # Cleanup temp_dir on error
        raise
    except Exception as e:
        logger.error(f"Unexpected error during media download for {url}, format {format_id}: {str(e)}", exc_info=True)
        shutil.rmtree(temp_dir, ignore_errors=True) # Cleanup temp_dir on error
        raise ValueError(f"An unexpected error occurred during download: {str(e)}")
