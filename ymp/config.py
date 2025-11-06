import configparser
import os

CONFIG_DIR = os.path.expanduser('~/.config/ymp')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.ini')

def get_config():
    """Reads the configuration file and returns a config object."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        create_default_config()
    config.read(CONFIG_FILE)
    return config

def create_default_config():
    """Creates a default configuration file."""
    config = configparser.ConfigParser()
    config['Settings'] = {
        'playlist_folder': os.path.expanduser('~/Music/ymp_playlists'),
        'download_folder': os.path.expanduser('~/Music/ymp_downloads'),
    }
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def get_playlist_folder():
    """Returns the playlist folder path from the config."""
    config = get_config()
    return config['Settings']['playlist_folder']

def get_download_folder():
    """Returns the download folder path from the config."""
    config = get_config()
    return config['Settings']['download_folder']
