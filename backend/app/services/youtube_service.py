import yt_dlp
import asyncio
import os
import tempfile
import logging
from typing import Dict, Any, Tuple, List
import shutil
import math

logger = logging.getLogger(__name__)

def _format_filesize(size_bytes: Optional[int]) -> str:
    if size_bytes is None or size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

async def _extract_yt_dlp_info(url: str, ydl_opts: Dict) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Run blocking IO in executor
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=ydl_opts.get('skip_download', True) is False))
            return info
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp DownloadError processing {url}: {str(e)}")
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
            filesize = f.get('filesize') or f.get('filesize_approx')
            filesize_str = _format_filesize(filesize)
            
            # Video formats (with audio, common containers)
            if (f.get('vcodec') != 'none' and f.get('acodec') != 'none' and 
                f.get('ext') in ['mp4', 'webm'] and filesize):
                video_formats.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'resolution': f.get('resolution') or f'{f.get("width")}x{f.get("height")}' or f.get('format_note'),
                    'filesize': filesize,
                    'filesize_str': filesize_str,
                    'fps': f.get('fps'),
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                    'note': f.get('format_note', '')
                })
            # Audio-only formats (common containers)
            elif (f.get('acodec') != 'none' and f.get('vcodec') == 'none' and 
                  f.get('ext') in ['m4a', 'mp3', 'opus', 'ogg', 'wav'] and filesize):
                audio_formats.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'filesize': filesize,
                    'filesize_str': filesize_str,
                    'acodec': f.get('acodec'),
                    'tbr': f.get('abr'), # Total Bitrate (abr is often used for audio bitrate in yt-dlp)
                    'note': f.get('format_note', '')
                })
    
    video_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize') or 0), reverse=True)
    audio_formats.sort(key=lambda x: (x.get('tbr') or 0, x.get('filesize') or 0), reverse=True)

    return {
        'id': info.get('id'),
        'title': info.get('title', 'N/A'),
        'thumbnail': info.get('thumbnail'),
        'description': info.get('description'),
        'duration': info.get('duration'),
        'duration_string': info.get('duration_string'),
        'channel': info.get('uploader') or info.get('channel'),
        'view_count': info.get('view_count'),
        'upload_date': info.get('upload_date'), # YYYYMMDD format
        'video_formats': video_formats,
        'audio_formats': audio_formats,
        'original_url': url # Added original_url
    }

async def download_media(url: str, format_id: str, media_type: str, filename_prefix: str) -> Tuple[str, str, str]:
    temp_dir = tempfile.mkdtemp(prefix='tubefetch_')
    
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': False,
    }

    try:
        info_dict = await _extract_yt_dlp_info(url, ydl_opts)
        
        downloaded_file_path = None
        if info_dict.get('requested_downloads') and len(info_dict['requested_downloads']) > 0:
            downloaded_file_path = info_dict['requested_downloads'][0].get('filepath')
        
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            logger.warning("'requested_downloads' not found or empty, attempting to find file in temp_dir")
            files_in_temp = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            if not files_in_temp:
                raise FileNotFoundError(f"yt-dlp finished but no file was found in the temp directory: {temp_dir}")
            # Sort by creation time or modification time might be better if multiple files could exist
            downloaded_file_path = max(files_in_temp, key=os.path.getmtime)
            logger.info(f"Fallback found downloaded file: {downloaded_file_path}")

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
             raise FileNotFoundError(f"Downloaded file path could not be determined or does not exist: {downloaded_file_path}")

        actual_filename_on_disk = os.path.basename(downloaded_file_path)
        logger.info(f"Media downloaded to: {downloaded_file_path} (Disk filename: {actual_filename_on_disk})")
        
        return temp_dir, downloaded_file_path, actual_filename_on_disk

    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Error during media download preparation for {url}, format {format_id}: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during media download for {url}, format {format_id}: {str(e)}", exc_info=True)
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError(f"An unexpected error occurred during download: {str(e)}")
