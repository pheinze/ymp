import ymp.downloader as downloader
import ymp.player as player
import os
import time


import random
from termcolor import colored
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

console = Console()

class Playlist:
    """Manages the playlist, including queuing, playback, and song history."""

    def __init__(self):
        """Initializes the Playlist object."""
        self.queuedplaylist=[]
        self.playedplaylist=[]
        self.starttime = None
        self.pausetime = None
        self.meta = None
        self.filepath = None
        self.playobj = None
        self.resumetime = None
        self.songpaused = False
        self.repeat = 0
        self.playback_progress = Progress(
            TextColumn("[bold green]Playing:"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TimeRemainingColumn(),
        )

    def returnsong(self):
        """Returns the next song from the queue and adds it to the played list."""
        song_info = self.queuedplaylist.pop(0)
        self.playedplaylist.append(song_info)

        if isinstance(song_info, dict):
            return song_info.get('url') or song_info.get('title')
        return song_info # It's already a string

    def addsong(self,query):
        """Adds a song to the queue."""
        # Check if it's just a search term
        if not query.startswith("http"):
            query += " song"
        self.queuedplaylist.append(query)

    def downloadsong(self,song,dir_path):
        """Downloads a song."""
        meta, filepath = downloader.download(song,dir_path)
        self.filepath = filepath
        return meta

    def shuffleplaylist(self):
            """Shuffles the queued playlist."""
            random.shuffle(self.queuedplaylist)
            console.print("Queue Shuffled", style="bold green")

    def playsong(self,meta,dir_path):
        """Plays a song."""
        self.meta=meta
        self.resumetime=0

        console.print(f"[bold yellow]Currently Playing:[/] {meta['title']}")

        self.playback_task = self.playback_progress.add_task("playback", total=meta.get('duration', 100))
        self.playback_progress.start()

        self.playobj,self.starttime=player.genmusic(self.filepath,0)

    def update_playback_progress(self):
        """Updates the playback progress bar."""
        if self.playobj and not self.songpaused:
            if self.starttime:
                elapsed = (time.time() - self.starttime) * 1000 + self.resumetime
                self.playback_progress.update(self.playback_task, completed=elapsed / 1000)

    def stop_playback_progress(self):
        """Stops and removes the playback progress bar."""
        self.playback_progress.stop()
        self.playback_progress.remove_task(self.playback_task)

    def resumesong(self,dir_path):
        """Resumes a paused song."""
        if self.songpaused==True:
            console.print(f"Resuming: {self.meta['title']}", style="yellow")
            self.playback_progress.start()
            self.playobj,self.starttime=player.genmusic(self.filepath,self.resumetime)
            self.songpaused=False
        else:
            console.print("Already Playing", style="bold red")

    def pausesong(self):
        """Pauses the current song."""
        if self.songpaused==True:
            console.print("Already Paused", style="bold red")
        else:
            self.songpaused=True
            self.pausetime=player.pausemusic(self.playobj)
            self.resumetime = self.resumetime+((self.pausetime - self.starttime)*1000)
            self.playback_progress.stop()

    def nextsong(self):
        """Skips to the next song."""
        self.stop_playback_progress()
        if self.repeat==2:
            self.repeat=0
            self.playobj.stop()
            self.songpaused=False
            player.wait()
            self.repeat=2
        else:
            self.playobj.stop()
            self.songpaused=False

    def shiftlastplayedsong(self):
        """Moves the last played song to the front of the queue."""
        self.queuedplaylist=[self.playedplaylist.pop()]+self.queuedplaylist

    def loopqueue(self):
        """Loops the queue by adding the played songs back to the queue."""
        self.queuedplaylist.extend(self.playedplaylist)
        self.playedplaylist.clear()

    def removelastqueuedsong(self):
        """Removes the last song from the queue."""
        try:
            self.queuedplaylist.pop()
        except:
            print("Empty queue")

    def previoussong(self):
        """Goes back to the previous song."""
        try:
            self.stop_playback_progress()
            self.queuedplaylist=[self.playedplaylist.pop()]+self.queuedplaylist
            self.queuedplaylist=[self.playedplaylist.pop()]+self.queuedplaylist
            self.playobj.stop()
            self.songpaused=False
        except:
            print(colored("Error: can't go back beyond start ",'red'))

    def repeatsong(self,mode):
        """Sets the repeat mode."""
        if mode == "off":
            self.repeat = 0
        elif mode == "all":
            self.repeat = 1
        elif mode == "song":
            self.repeat = 2
        else:
            print(colored("Error: Invalid Mode ",'red'))

    def seeksong(self,value,dir_path):
        """Seeks forward or backward in the current song."""
        if self.songpaused==False:
            self.pausesong()
        self.resumetime=self.resumetime + (value*1000)
        self.resumesong(dir_path)

    def returnplaylist(self):
        """Returns the entire playlist (played and queued songs)."""
        allplaylist=self.playedplaylist+self.queuedplaylist
        return allplaylist
