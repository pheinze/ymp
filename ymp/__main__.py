import warnings
import ymp.downloader as downloader
from ymp.playlistmanager import Playlist
from ymp.player import wait
import ymp.config as config


import threading, argparse, json, sys, os
import subprocess
from urllib import request

from pyfiglet import Figlet
from colorama import init,deinit
from termcolor import colored

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
        # It's a single video, add its URL as a string.
        # The download function will handle fetching the metadata.
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
        # Condition 1: A song has just finished playing
        if musicplaylist.playobj and not musicplaylist.playobj.is_playing() and not musicplaylist.songpaused:
            musicplaylist.stop_playback_progress()

            # Case 1.1: Repeat current song
            if musicplaylist.repeat == 2:
                musicplaylist.shiftlastplayedsong()
                startmusic()
            # Case 1.2: Songs are in the queue
            elif musicplaylist.queuedplaylist:
                startmusic()
            # Case 1.3: Loop the entire playlist
            elif musicplaylist.repeat == 1:
                musicplaylist.loopqueue()
                if musicplaylist.queuedplaylist:
                    startmusic()
            # Case 1.4: Nothing to play
            else:
                if not interactive:
                    # Playlist finished, exit gracefully
                    break
                songavailable.clear()
                songavailable.wait()

        # Condition 2: No song is currently playing or paused, but there are songs in the queue
        elif not musicplaylist.playobj and not musicplaylist.songpaused and musicplaylist.queuedplaylist:
            startmusic()

        # Condition 3: A song is playing, update the progress bar
        elif musicplaylist.playobj and musicplaylist.playobj.is_playing() and not musicplaylist.songpaused:
            musicplaylist.update_playback_progress()

        # Condition 4: The player is paused or idle
        else:
            # If nothing is happening, wait for a new song if the queue is empty
            if not musicplaylist.queuedplaylist and not musicplaylist.playobj:
                songavailable.clear()
                songavailable.wait()

        time.sleep(0.5)

def queue():
    """Handles user input for controlling the music player."""
    while True:
        request=input("")
        if request=="exit":
            deinit()
            downloader.removedownload(dir)
            sys.exit()

        elif request=="" or request==" ":
            pass

        elif request=="shuffle":
            if musicplaylist.queuedplaylist:
                musicplaylist.shuffleplaylist()
            else:
                print("Cannot Shuffle Empty Queue")

        elif request=="play":
            musicplaylist.resumesong(dir_path)
            songavailable.set()

        elif request=="pause":
            musicplaylist.pausesong()

        elif request=="next":
            musicplaylist.nextsong()

        elif request=="back":
            musicplaylist.previoussong()

        elif request=="rm":
            musicplaylist.removelastqueuedsong()

        elif request.startswith("repeat"):
            parts = request.split()
            if len(parts) > 1:
                mode = parts[1]
                musicplaylist.repeatsong(mode)

        elif request.startswith("seek"):
            parts = request.split()
            if len(parts) > 1:
                value = parts[1]
                try:
                    value = int(value)
                    musicplaylist.seeksong(value,dir_path)
                except:
                    print("Error: Invalid seek value ",'red')

        elif request == "download":
            song_to_download = musicplaylist.playedplaylist[-1]
            download_dir = downloader.makedownload(permanent=True)
            downloader.download(song_to_download, download_dir)

        elif request=="spotify":
            spotifyplaylistlink=input("Enter Playlist: ")
            playspotify(spotifyplaylistlink)

        elif request=="youtube":
            ytplaylist=input("Enter Playlist: ")
            playyoutube(ytplaylist)

        elif request=="save":
            playlistname=input("Enter Playlist Name: ")
            saveplaylist(playlistname)

        elif request=="load":
            playlistname=input("Enter Playlist Name: ")
            loadplaylist(playlistname)

        elif request=="commands":
            print("Type spotify to play music using spotify playlist")
            print("Type youtube to play music using youtube playlist")
            print("Use rm to remove the last queued song from the playlist.")
            print("Type shuffle to shuffle your queue.")
            print("Use load to load a playlist and save to save your playlist.")
            print("Use play , pause, next, back to control the playback.")
            print("Use repeat all, repeat song and repeat offto control song repetition.")
            print("Use seek with an integer like 10 or -10 to control the current song.")
            print("To exit the command window and hence the application simply type exit.")

        else:
            musicplaylist.addsong(request)
            songavailable.set()


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
        # Get the latest commit hash from the master branch on GitHub
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
                    # After a successful upgrade, save the new commit hash
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

    f = Figlet(font='banner3-D')
    print(" ")
    print(colored(f.renderText('YMP'),'cyan'))
    print("\t\t\t\t\t\t- by pheinze")

    from . import __version__
    parser = argparse.ArgumentParser(prog='ymp', description='Your Music Player',epilog='Thank you for using YMP! :)')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument("-s", action='store', metavar='link', help="Play a Spotify Playlist")
    parser.add_argument("-y", action='store', metavar='link', help="Play a Youtube Playlist")
    parser.add_argument("-p", action='store', nargs='+', metavar='song', help="Play multiple youtube links or a songs")
    parser.add_argument("-l", action='store', metavar='playlistname', help="Play a ymp generated playlist")
    # This -v is redundant, version is already handled
    # parser.add_argument('-v', action='version')
    parser.add_argument('-u', '--update', action='store_true', help="Check for updates")
    args = parser.parse_args()

    if args.update:
        check_for_updates()
        sys.exit()

    interactive_mode = not (args.s or args.y or args.l or args.p)

    # Pass the mode to the play function
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
        queuethread=threading.Thread(target=queue)
        queuethread.start()
        try:
            queuethread.join()
        except KeyboardInterrupt:
            print("\nExiting...")
            deinit()
            downloader.removedownload(dir_obj)
            sys.exit()
    else:
        # Non-interactive mode: wait for the playlist to finish
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
