from yt_dlp import YoutubeDL
from requests import get
from bs4 import BeautifulSoup
import re , json ,tempfile, os
import ymp.config as config
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeElapsedColumn

def spotifyparser(url):
    """
    Parses a Spotify playlist URL to extract track information.

    Note: This method is fragile as it relies on scraping the Spotify website,
    which can change at any time. A more robust solution would use the Spotify API.
    """
    print("Pinging "+url)
    spotifyhtml=get(url)
    soup=BeautifulSoup(spotifyhtml.content,"lxml")
    tags=soup('script')
    x=re.findall("Spotify.Entity = (.*);",tags[5].contents[0])
    data=x[0]
    jsonfile=json.loads(data)

    print("Adding "+jsonfile['name']+" To Queue." )
    tracks=jsonfile['tracks']['items']

    tracklist=[]

    for track in tracks:
        trackname=track['track']['name']
        artistname=""
        for artist in track['track']['artists']:
            artistname=artistname+" "+artist['name']
        tracklist.append(trackname+artistname)

    return tracklist

def get_playlist_info(url):
    """Extracts video info from a playlist URL without downloading."""
    options = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(options) as ytdl:
        try:
            meta = ytdl.extract_info(url, download=False)
            return meta.get('entries', [])
        except Exception as e:
            print(f"Error fetching playlist info: {e}")
            return []

def download(link,dir_path):
    """Downloads a song from YouTube using yt-dlp."""
    progress = Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        TransferSpeedColumn(),
        "•",
        TimeElapsedColumn(),
    )

    with progress:
        task = progress.add_task("download", filename=link, total=100)

        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)

                progress.update(
                    task,
                    total=total_bytes,
                    completed=downloaded_bytes,
                    description=f"[cyan]Downloading at {speed_text(speed)}"
                )

            if d['status'] == 'finished':
                progress.update(task, description="[green]Processing...", completed=d.get('total_bytes', 100))

        options={
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(dir_path, '%(artist)s - %(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }, {
                'key': 'EmbedThumbnail',
            }],
            'writethumbnail': True,
            'add_metadata': True,
            'default_search': 'ytsearch',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'noprogress': True,
            'no_warnings': True,
        }

        filepath = None
        with YoutubeDL(options) as ytdl:
            try:
                meta = ytdl.extract_info(link, download=True)
                if 'entries' in meta:
                    meta = meta['entries'][0]

                progress.update(task, filename=meta.get('title', link))
                filepath = ytdl.prepare_filename(meta)
                filepath = os.path.splitext(filepath)[0] + '.mp3'

            except Exception as e:
                progress.update(task, description=f"[red]Error: {e}")
                return None, None

    return meta, filepath

def speed_text(speed):
    if speed is None:
        return ""
    return f"{speed / 1024:.1f} KiB/s"

def makedownload(permanent=False):
    """Creates a temporary or permanent directory for downloading songs."""
    if permanent:
        download_folder = config.get_download_folder()
        os.makedirs(download_folder, exist_ok=True)
        return download_folder
    else:
        return tempfile.TemporaryDirectory()

def removedownload(dir):
    """Removes the temporary download directory if it is one."""
    if isinstance(dir, tempfile.TemporaryDirectory):
        try:
            dir.cleanup()
        except:
            pass