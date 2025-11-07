import warnings
from . import downloader
from .playlistmanager import Playlist
from .player import wait
from . import config


import threading, argparse, json, sys, os
import subprocess
from urllib import request

from pyfiglet import Figlet
from colorama import init,deinit
from termcolor import colored
from .tui import YmpApp

musicplaylist = Playlist()
songavailable = threading.Event()

dir_obj=downloader.makedownload()
dir_path = dir_obj.name if hasattr(dir_obj, 'name') else dir_obj


def playspotify(link):
    """Parses a Spotify playlist and adds the songs to the queue."""
    spotifyplaylist=downloader.spotifyparser(link)
    musicplaylist.queuedplaylist.extend(spotifyplaylist)
    songavailable.set()

def playyoutube(link):
    """Fetches info for a YouTube playlist/video and adds it to the queue."""
    if "list=" in link:
        print("Fetching playlist info...")
        playlist_items = downloader.get_playlist_info(link)
        if playlist_items:
            musicplaylist.queuedplaylist.extend(playlist_items)
            print(f"Added {len(playlist_items)} songs to the queue.")
            songavailable.set()
    else:
        musicplaylist.addsong(link)
        songavailable.set()

def saveplaylist(name):
    """Saves the current playlist to a JSON file."""
    path = config.get_playlist_folder()
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    filepath = os.path.join(path, f'{name}.json')
    playlist_data = musicplaylist.returnplaylist()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(playlist_data, f, ensure_ascii=False, indent=4)
    print(f"Playlist '{name}' successfully saved to {filepath}")

def loadplaylist(name):
    """Loads a playlist from a JSON file."""
    path = config.get_playlist_folder()
    filepath = os.path.join(path, f'{name}.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            playlist_data = json.load(f)
            musicplaylist.queuedplaylist.extend(playlist_data)
            print(f"Successfully loaded playlist '{name}'")
            songavailable.set()
    except FileNotFoundError:
        print(colored(f"Playlist '{name}' not found at {filepath}", 'red'))
    except json.JSONDecodeError:
        print(colored(f"Error decoding playlist file: {filepath}", 'red'))

def startmusic():
    """Downloads and plays the next song in the queue."""
    song=musicplaylist.returnsong()
    meta=musicplaylist.downloadsong(song,dir_path)
    if meta:
        musicplaylist.playsong(meta,dir_path)
    else:
        print(colored(f"Could not download '{song}'. Skipping.", 'red'))

import time

def play(interactive=True):
    """Main loop for music playback."""
    while True:
        if musicplaylist.playobj and not musicplaylist.playobj.is_playing() and not musicplaylist.songpaused:
            musicplaylist.stop_playback_progress()

            if musicplaylist.repeat == 2:
                musicplaylist.shiftlastplayedsong()
                startmusic()
            elif musicplaylist.queuedplaylist:
                startmusic()
            elif musicplaylist.repeat == 1:
                musicplaylist.loopqueue()
                if musicplaylist.queuedplaylist:
                    startmusic()
            else:
                if not interactive:
                    break
                songavailable.clear()
                songavailable.wait()

        elif not musicplaylist.playobj and not musicplaylist.songpaused and musicplaylist.queuedplaylist:
            startmusic()

        elif musicplaylist.playobj and musicplaylist.playobj.is_playing() and not musicplaylist.songpaused:
            musicplaylist.update_playback_progress()

        else:
            if not musicplaylist.queuedplaylist and not musicplaylist.playobj:
                songavailable.clear()
                songavailable.wait()

        time.sleep(0.5)

def get_local_commit_path():
    """Gets the path to the file storing the local commit hash."""
    return os.path.join(config.CONFIG_DIR, 'version.txt')

def get_local_commit():
    """Reads the locally stored git commit hash."""
    path = get_local_commit_path()
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return f.read().strip()

def save_local_commit(commit_hash):
    """Saves the git commit hash of the current version."""
    path = get_local_commit_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(commit_hash)

def check_for_updates():
    """Checks for updates on GitHub and offers to upgrade."""
    print("Checking for updates...")
    try:
        url = "https://api.github.com/repos/pheinze/ymp/branches/master"
        with request.urlopen(url, timeout=5) as response:
            data = json.load(response)
            latest_commit = data['commit']['sha']

        local_commit = get_local_commit()

        if not local_commit:
            print(colored("Could not determine local version. Cannot check for updates.", "red"))
            return

        if latest_commit != local_commit:
            print(colored("A new version is available!", "yellow"))
            upgrade = input("Do you want to upgrade? (y/n): ").lower().strip()
            if upgrade == 'y':
                print("Upgrading from GitHub with pipx...")
                try:
                    subprocess.run(
                        ["pipx", "install", "--force", "git+https://github.com/pheinze/ymp.git"],
                        check=True
                    )
                    save_local_commit(latest_commit)
                    print(colored("Update successful! Please restart ymp if it was already running.", "green"))
                    sys.exit()
                except subprocess.CalledProcessError as e:
                    print(colored(f"Update failed: {e}", "red"))
                except FileNotFoundError:
                    print(colored("`pipx` command not found. Please upgrade manually.", "red"))
            else:
                print("Update skipped.")
        else:
            print(colored("You are using the latest version.", "green"))

    except Exception as e:
        print(colored(f"Could not check for updates: {e}", "red"))

def main():
    init()

    from . import __version__
    parser = argparse.ArgumentParser(prog='ymp', description='Your Music Player',epilog='Thank you for using YMP! :)')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument("-s", action='store', metavar='link', help="Play a Spotify Playlist")
    parser.add_argument("-y", action='store', metavar='link', help="Play a Youtube Playlist")
    parser.add_argument("-p", action='store', nargs='+', metavar='song', help="Play multiple youtube links or a songs")
    parser.add_argument("-l", action='store', metavar='playlistname', help="Play a ymp generated playlist")
    parser.add_argument('-u', '--update', action='store_true', help="Check for updates")
    args = parser.parse_args()

    if args.update:
        check_for_updates()
        sys.exit()

    interactive_mode = not (args.s or args.y or args.l or args.p)

    playthread=threading.Thread(target=play, args=(interactive_mode,), daemon=True)
    playthread.start()

    if args.s:
        playspotify(args.s)
    if args.y:
        playyoutube(args.y)
    if args.l:
        loadplaylist(args.l)
    if args.p:
        for songs in args.p:
            musicplaylist.addsong(songs)
        songavailable.set()

    if interactive_mode:
        f = Figlet(font='banner3-D')
        print(" ")
        print(colored(f.renderText('YMP'),'cyan'))
        print("\t\t\t\t\t\t- by pheinze")
        app = YmpApp(playlist=musicplaylist)
        app.run()
        deinit()
        downloader.removedownload(dir_obj)
        sys.exit()
    else:
        try:
            playthread.join()
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            deinit()
            downloader.removedownload(dir_obj)
            sys.exit(0)

if __name__ == "__main__":
    main()
