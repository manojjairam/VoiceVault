import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp


# ============================================================
# URL DETECTION
# ============================================================

def detect_url_type(url):
    """
    Detect the type of online source.

    Returns:
        youtube
        google_meet
        direct_media
        unknown
    """

    if not url:
        return "unknown"

    url = url.strip().lower()

    # Google Meet
    if "meet.google.com" in url:
        return "google_meet"

    # YouTube
    youtube_patterns = [
        "youtube.com/watch",
        "youtube.com/shorts",
        "youtube.com/live",
        "youtube.com/embed",
        "youtu.be/",
        "youtube-nocookie.com/"
    ]

    if any(pattern in url for pattern in youtube_patterns):
        return "youtube"

    # Direct media extensions
    media_extensions = (
        ".mp3",
        ".wav",
        ".m4a",
        ".aac",
        ".ogg",
        ".flac",
        ".opus",
        ".mp4",
        ".mkv",
        ".webm",
        ".mov",
        ".avi",
        ".flv",
        ".wmv",
        ".m4v",
        ".3gp",
    )

    parsed = urlparse(url)
    path = parsed.path.lower()

    if any(path.endswith(ext) for ext in media_extensions):
        return "direct_media"

    return "unknown"


# ============================================================
# FFMPEG CHECK
# ============================================================

def check_ffmpeg():
    """
    Check whether FFmpeg is available.
    """

    return shutil.which("ffmpeg") is not None


# ============================================================
# DENO CHECK
# ============================================================

def check_deno():
    """
    Check whether Deno is available.

    Deno is used by modern yt-dlp versions to solve
    JavaScript challenges encountered by YouTube.
    """

    return shutil.which("deno") is not None


# ============================================================
# FORMAT DURATION
# ============================================================

def format_duration(seconds):
    """
    Convert seconds into HH:MM:SS or MM:SS.
    """

    try:

        seconds = int(seconds or 0)

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return f"{minutes:02d}:{seconds:02d}"

    except Exception:

        return "Unknown"


# ============================================================
# STREAM DETECTION
# ============================================================

def has_video_stream(info):
    """
    Determine whether the media contains a video stream.
    """

    if not isinstance(info, dict):
        return False

    formats = info.get("formats", [])

    for fmt in formats:

        if fmt.get("vcodec") not in (None, "none"):
            return True

    return False


def has_audio_stream(info):
    """
    Determine whether the media contains an audio stream.
    """

    if not isinstance(info, dict):
        return False

    formats = info.get("formats", [])

    for fmt in formats:

        if fmt.get("acodec") not in (None, "none"):
            return True

    return False


# ============================================================
# LANGUAGE INFORMATION
# ============================================================

def get_detected_language(info):
    """
    Try to determine the language associated with the media.

    YouTube metadata may contain language information.
    If unavailable, Whisper will determine the language
    during transcription.
    """

    if not isinstance(info, dict):
        return "Unknown"

    possible_fields = [
        "language",
        "language_preference",
    ]

    for field in possible_fields:

        value = info.get(field)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return "Unknown"


# ============================================================
# GET MEDIA INFORMATION
# ============================================================

def get_media_information(url):
    """
    Retrieve online media metadata without downloading it.

    For YouTube, Deno is explicitly configured for yt-dlp.
    """

    url = url.strip()

    if not url:

        return {
            "success": False,
            "error": "Please enter a URL."
        }

    source_type = detect_url_type(url)

    # Google Meet
    if source_type == "google_meet":

        return {
            "success": False,
            "source_type": "google_meet",
            "error": (
                "A normal Google Meet URL is a meeting page, "
                "not a downloadable recording URL. "
                "Please provide the actual accessible recording "
                "URL or upload the recording."
            )
        }

    if source_type == "youtube" and not check_deno():

        return {
            "success": False,
            "source_type": "youtube",
            "error": (
                "Deno is not available. "
                "Install Deno and restart the terminal before "
                "processing YouTube URLs."
            )
        }

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,

        # Modern YouTube JavaScript challenge support
        "js_runtimes": {
            "deno": {}
        },

        # Use the installed EJS package
        "remote_components": {
            "ejs:github"
        },
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        if not info:

            return {
                "success": False,
                "source_type": source_type,
                "error": "Could not retrieve media information."
            }

        duration = info.get("duration") or 0

        return {
            "success": True,
            "title": info.get("title", "Unknown"),
            "description": info.get("description", ""),
            "duration": duration,
            "duration_string": format_duration(duration),
            "uploader": info.get("uploader", "Unknown"),
            "channel": info.get("channel", ""),
            "channel_id": info.get("channel_id", ""),
            "upload_date": info.get("upload_date", ""),
            "webpage_url": info.get(
                "webpage_url",
                url
            ),
            "thumbnail": info.get("thumbnail", ""),
            "source_type": source_type,
            "has_video": has_video_stream(info),
            "has_audio": has_audio_stream(info),
            "language": get_detected_language(info),
            "view_count": info.get("view_count"),
            "categories": info.get("categories", []),
            "tags": info.get("tags", []),
        }

    except Exception as e:

        return {
            "success": False,
            "source_type": source_type,
            "error": str(e)
        }


# ============================================================
# FIND DOWNLOADED FILE
# ============================================================

def find_media_file(directory):
    """
    Find the actual downloaded media file inside a directory.

    This is intentionally more reliable than assuming that
    yt-dlp always produces a particular filename.
    """

    if not directory or not os.path.isdir(directory):
        return None

    ignored_extensions = {
        ".part",
        ".ytdl",
        ".json",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".vtt",
        ".srt",
        ".ass",
    }

    files = []

    for filename in os.listdir(directory):

        full_path = os.path.join(
            directory,
            filename
        )

        if not os.path.isfile(full_path):
            continue

        extension = Path(filename).suffix.lower()

        if extension in ignored_extensions:
            continue

        if os.path.getsize(full_path) <= 0:
            continue

        files.append(full_path)

    if not files:
        return None

    # Prefer audio files
    audio_extensions = {
        ".wav",
        ".mp3",
        ".m4a",
        ".aac",
        ".ogg",
        ".opus",
        ".flac",
        ".webm",
    }

    audio_files = [
        path
        for path in files
        if Path(path).suffix.lower() in audio_extensions
    ]

    if audio_files:

        return max(
            audio_files,
            key=os.path.getsize
        )

    # Otherwise return the largest media file
    return max(
        files,
        key=os.path.getsize
    )


# ============================================================
# DOWNLOAD ONLINE MEDIA
# ============================================================

def download_online_media(url):
    """
    Download online media for VoiceVault.

    YouTube:
        - Uses Deno + yt-dlp-ejs
        - Downloads audio only
        - Converts audio to WAV

    Other supported media:
        - Attempts audio extraction
        - Returns a valid local audio file
    """

    url = url.strip()

    if not url:

        return {
            "success": False,
            "error": "Please enter a URL."
        }

    source_type = detect_url_type(url)

    # --------------------------------------------------------
    # Google Meet
    # --------------------------------------------------------

    if source_type == "google_meet":

        return {
            "success": False,
            "source_type": "google_meet",
            "error": (
                "A normal Google Meet URL cannot be downloaded "
                "directly because it is a meeting page. "
                "Please provide the actual accessible recording "
                "URL or upload the recording."
            )
        }

    # --------------------------------------------------------
    # FFmpeg
    # --------------------------------------------------------

    if not check_ffmpeg():

        return {
            "success": False,
            "source_type": source_type,
            "error": (
                "FFmpeg was not found. "
                "Please install FFmpeg and add it to PATH."
            )
        }

    # --------------------------------------------------------
    # Deno for YouTube
    # --------------------------------------------------------

    if source_type == "youtube" and not check_deno():

        return {
            "success": False,
            "source_type": source_type,
            "error": (
                "Deno was not found. "
                "YouTube processing requires Deno with the "
                "current yt-dlp JavaScript challenge system."
            )
        }

    # --------------------------------------------------------
    # Temporary directory
    # --------------------------------------------------------

    output_directory = tempfile.mkdtemp(
        prefix="voicevault_media_"
    )

    output_template = os.path.join(
        output_directory,
        "voicevault_source.%(ext)s"
    )

    # --------------------------------------------------------
    # yt-dlp configuration
    # --------------------------------------------------------

    ydl_opts = {
        # Audio-first
        "format": "bestaudio/best",

        "outtmpl": output_template,

        "noplaylist": True,

        "quiet": True,

        "no_warnings": True,

        # Modern YouTube JS challenge solving
        "js_runtimes": {
            "deno": {}
        },

        # yt-dlp EJS
        "remote_components": {
            "ejs:github"
        },

        # Convert audio to WAV
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        # FFmpeg audio settings
        "postprocessor_args": [
            "-ar",
            "16000",
            "-ac",
            "1",
        ],

        # Do not download playlists
        "noplaylist": True,
    }

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

        if not info:

            raise RuntimeError(
                "yt-dlp did not return media information."
            )

        # ----------------------------------------------------
        # Locate generated WAV
        # ----------------------------------------------------

        wav_files = []

        for filename in os.listdir(output_directory):

            if filename.lower().endswith(".wav"):

                path = os.path.join(
                    output_directory,
                    filename
                )

                if os.path.isfile(path) and os.path.getsize(path) > 0:
                    wav_files.append(path)

        if wav_files:

            audio_path = max(
                wav_files,
                key=os.path.getsize
            )

        else:

            # ------------------------------------------------
            # Fallback
            # ------------------------------------------------

            downloaded_file = find_media_file(
                output_directory
            )

            if not downloaded_file:

                raise RuntimeError(
                    "yt-dlp completed but no media file was "
                    "created."
                )

            # ------------------------------------------------
            # Convert manually to WAV
            # ------------------------------------------------

            audio_path = os.path.join(
                output_directory,
                "voicevault_audio.wav"
            )

            command = [
                "ffmpeg",
                "-y",
                "-i",
                downloaded_file,
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                audio_path,
            ]

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:

                raise RuntimeError(
                    "FFmpeg failed to convert the downloaded "
                    "media to WAV.\n\n"
                    + result.stderr
                )

        # ----------------------------------------------------
        # Validate audio
        # ----------------------------------------------------

        if not os.path.exists(audio_path):

            raise RuntimeError(
                "Audio file was not created."
            )

        if os.path.getsize(audio_path) <= 0:

            raise RuntimeError(
                "The generated audio file is empty."
            )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        title = info.get(
            "title",
            "Online Media"
        )

        duration = info.get(
            "duration",
            0
        )

        original_has_video = has_video_stream(
            info
        )

        original_has_audio = has_audio_stream(
            info
        )

        detected_language = get_detected_language(
            info
        )

        # ----------------------------------------------------
        # Determine original media type
        # ----------------------------------------------------

        if original_has_video:

            detected_media_type = "video"

        elif original_has_audio:

            detected_media_type = "audio"

        else:

            detected_media_type = "unknown"

        # ----------------------------------------------------
        # Return complete result
        # ----------------------------------------------------

        return {
            "success": True,

            "audio_path": audio_path,

            "title": title,

            "description": info.get(
                "description",
                ""
            ),

            "duration": duration,

            "duration_string": format_duration(
                duration
            ),

            "uploader": info.get(
                "uploader",
                "Unknown"
            ),

            "channel": info.get(
                "channel",
                ""
            ),

            "channel_id": info.get(
                "channel_id",
                ""
            ),

            "upload_date": info.get(
                "upload_date",
                ""
            ),

            "webpage_url": info.get(
                "webpage_url",
                url
            ),

            "thumbnail": info.get(
                "thumbnail",
                ""
            ),

            "source_type": source_type,

            "media_type": detected_media_type,

            "has_video": original_has_video,

            "has_audio": original_has_audio,

            "language": detected_language,

            "view_count": info.get(
                "view_count"
            ),

            "categories": info.get(
                "categories",
                []
            ),

            "tags": info.get(
                "tags",
                []
            ),

            "directory": output_directory,
        }

    except Exception as e:

        # Clean up failed download
        shutil.rmtree(
            output_directory,
            ignore_errors=True
        )

        error_message = str(e)

        # Make YouTube errors more understandable
        if "CERTIFICATE_VERIFY_FAILED" in error_message:

            error_message = (
                "SSL certificate verification failed while "
                "connecting to the media source. "
                "Please check your Windows certificates, "
                "Python environment and network configuration."
            )

        elif "not available" in error_message.lower():

            error_message = (
                "The media could not be accessed by yt-dlp. "
                "The URL may be private, restricted, age-restricted, "
                "region-restricted, or require authentication."
            )

        return {
            "success": False,
            "source_type": source_type,
            "error": error_message,
        }


# ============================================================
# VIDEO → AUDIO
# ============================================================

def extract_audio_from_video(video_path):
    """
    Extract audio from an already downloaded/uploaded video.

    Output:
        16 kHz
        mono
        PCM WAV

    This format is ideal for local speech-recognition models.
    """

    if not video_path:

        return {
            "success": False,
            "error": "No video path was provided."
        }

    if not isinstance(
        video_path,
        (str, os.PathLike)
    ):

        return {
            "success": False,
            "error": "Invalid video path."
        }

    video_path = str(video_path)

    if not os.path.exists(video_path):

        return {
            "success": False,
            "error": "Video file does not exist."
        }

    output_path = (
        os.path.splitext(video_path)[0]
        + "_audio.wav"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        output_path,
    ]

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:

            return {
                "success": False,
                "error": result.stderr
            }

        if not os.path.exists(output_path):

            return {
                "success": False,
                "error": "Audio extraction failed."
            }

        if os.path.getsize(output_path) <= 0:

            return {
                "success": False,
                "error": "Extracted audio file is empty."
            }

        return {
            "success": True,
            "audio_path": output_path
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }