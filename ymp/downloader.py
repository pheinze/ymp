import os
import tempfile
import yt_dlp
from termcolor import colored
from . import config

def makedownload(permanent=False):
    """Creates a temporary or permanent directory for downloads."""
    if permanent:
        return config.get_download_folder()
    return tempfile.TemporaryDirectory()

def removedownload(dir_obj):
    """Removes a temporary directory."""
    if isinstance(dir_obj, tempfile.TemporaryDirectory):
        try:
            dir_obj.cleanup()
        except Exception as e:
            print(colored(f"Could not clean up temporary directory: {e}", "red"))

def download(song, dir_path):
    """Downloads a song from YouTube."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(dir_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        },{
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        },{
            'key': 'EmbedThumbnail',
        }],
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song, download=True)
            if 'entries' in info:
                info = info['entries'][0]

            # Construct the filename yt-dlp *would* create
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            mp3_filepath = f"{base}.mp3"

            # Check if download was successful
            if not os.path.exists(mp3_filepath):
                 print(colored(f"Error: Downloaded file not found at '{mp3_filepath}'", "red"))
                 return None, None

            return info, mp3_filepath

    except Exception as e:
        print(colored(f"Error downloading '{song}': {e}", "red"))
        return None, None

def get_playlist_info(playlist_url):
    """Fetches metadata for all items in a YouTube playlist."""
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_dict = ydl.extract_info(playlist_url, download=False)
            return playlist_dict.get('entries', [])
    except Exception as e:
        print(colored(f"Error fetching playlist info: {e}", "red"))
        return []
