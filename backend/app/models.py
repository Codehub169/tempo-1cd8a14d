from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class FormatDetail(BaseModel):
    format_id: str
    ext: str
    resolution: Optional[str] = None # For video, e.g., "1920x1080"
    # quality_label: Optional[str] = None # e.g., 720p, 1080p - covered by resolution or note
    filesize: Optional[int] = None
    filesize_str: Optional[str] = None # Human-readable filesize, e.g., "10.5 MB"
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    note: Optional[str] = None # yt-dlp's format_note, e.g. "1080p", "medium", "ultralow"
    tbr: Optional[float] = None # Total bitrate or average bitrate for audio (abr)
    fps: Optional[int] = None # Frames per second for video

class YouTubeVideoInfo(BaseModel):
    id: str
    title: str
    thumbnail: Optional[HttpUrl] = None
    channel: Optional[str] = None
    duration: Optional[int] = None # Duration in seconds
    duration_string: Optional[str] = None # Human-readable duration, e.g., "10:32"
    view_count: Optional[int] = None
    upload_date: Optional[str] = None # YYYYMMDD format
    description: Optional[str] = None
    video_formats: List[FormatDetail] = []
    audio_formats: List[FormatDetail] = []
    original_url: HttpUrl # The original URL passed by the client

class InstagramReelInfo(BaseModel):
    id: str
    uploader: Optional[str] = None
    uploader_id: Optional[str] = None
    title: Optional[str] = None # Often the full caption or a title if available
    description: Optional[str] = None # Full caption/description from yt-dlp
    thumbnail: Optional[HttpUrl] = None
    preview_image_url: Optional[HttpUrl] = None # Alias for thumbnail for frontend consistency
    duration: Optional[float] = None # Duration in seconds
    upload_date: Optional[str] = None # YYYYMMDD format
    direct_video_url: Optional[HttpUrl] = None # If yt-dlp provides a direct media link
    original_url: HttpUrl # The original URL passed by the client
    caption: Optional[str] = None # Shortened caption for display purposes

class ErrorResponse(BaseModel):
    detail: str

# DownloadSuccessResponse is not used by current router responses, FileResponse is used directly.
# If a JSON response for success was needed, it would be defined here.
# class DownloadSuccessResponse(BaseModel):
#     message: str
#     file_path: Optional[str] = None # Path on server, for debugging or internal use
#     filename: str # Suggested filename for client

# InfoRequest, YouTubeDownloadRequest, InstagramDownloadRequest are removed as they are not directly used
# as Pydantic models for request bodies in the current router setup (params are query params).
# If POST requests with JSON bodies were used for these operations, these models would be relevant.
