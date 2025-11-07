import configparser
import os

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "ymp")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")
PLAYLIST_DIR = os.path.join(CONFIG_DIR, "playlists")
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "ymp")

def get_config():
    """Reads the config file and returns the config object."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        create_default_config()
    config.read(CONFIG_FILE)
    return config

def create_default_config():
    """Creates the default config file."""
    config = configparser.ConfigParser()
    config["Settings"] = {
        "playlist_folder": PLAYLIST_DIR,
        "download_folder": DOWNLOAD_DIR,
    }
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

def get_playlist_folder():
    """Returns the playlist folder path from the config."""
    config = get_config()
    path = config.get("Settings", "playlist_folder", fallback=PLAYLIST_DIR)
    os.makedirs(path, exist_ok=True)
    return path

def get_download_folder():
    """Returns the download folder path from the config."""
    config = get_config()
    path = config.get("Settings", "download_folder", fallback=DOWNLOAD_DIR)
    os.makedirs(path, exist_ok=True)
    return path
