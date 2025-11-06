import ymp.downloader as downloader
from ymp.playlistmanager import Playlist
from ymp.player import wait
import ymp.config as config


import threading, argparse, json, sys, os

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
    """Parses a YouTube playlist or video and adds the songs to the queue."""
    if "list=" in link:
        beg=1
        while beg!=-1:
            tempytplaylist,beg=downloader.ytplaylistparser(link,beg)
            musicplaylist.queuedplaylist.extend(tempytplaylist)
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

def play():
    """Main loop for music playback."""
    while True:
        try:
            if musicplaylist.playobj and musicplaylist.playobj.is_playing():
                musicplaylist.playobj.wait_done()
        except:
            pass
        
        if  musicplaylist.songpaused==True:
            wait()

        elif musicplaylist.repeat==2:
            musicplaylist.shiftlastplayedsong()
            startmusic()

        elif musicplaylist.queuedplaylist :    
            startmusic()

        else:
            if musicplaylist.repeat==1:
                musicplaylist.loopqueue()

            else:
                songavailable.clear()
                songavailable.wait()

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
        

# Thread for music playback
playthread=threading.Thread(target=play,daemon=True)
# Thread for handling user input
queuethread=threading.Thread(target=queue)

def main():
    init()

    f = Figlet(font='banner3-D')
    print(" ")
    print(colored(f.renderText('YMP'),'cyan'))
    print("\t\t\t\t\t\t- by pheinze")

    parser = argparse.ArgumentParser(prog='ymp', description='Your Music Player',epilog='Thank you for using YMP! :)')
    parser.version = '0.4.0'
    parser.add_argument("-s", action='store', metavar='link', help="Play a Spotify Playlist")
    parser.add_argument("-y", action='store', metavar='link', help="Play a Youtube Playlist")
    parser.add_argument("-p", action='store', nargs='+', metavar='song', help="Play multiple youtube links or a songs")
    parser.add_argument("-l", action='store', metavar='playlistname', help="Play a ymp generated playlist")
    parser.add_argument('-v', action='version')
    args = parser.parse_args()

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

    queuethread.start()
    try:
        queuethread.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        deinit()
        downloader.removedownload(dir_obj)
        sys.exit()

if __name__ == "__main__":
    main()
