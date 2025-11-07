from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input
from textual.message import Message

_app_instance = None

def get_app():
    """Returns the running YmpApp instance."""
    return _app_instance

class YmpApp(App):
    """A Textual app to manage ymp playback."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("p", "toggle_pause", "Pause/Play"),
        ("n", "next_song", "Next"),
        ("b", "prev_song", "Back"),
        ("s", "shuffle", "Shuffle"),
        ("a", "add_song", "Add Song"),
    ]

    class PlaylistUpdated(Message):
        """Custom message to signal a playlist update."""
        pass

    def __init__(self, playlist, **kwargs):
        super().__init__(**kwargs)
        self.playlist = playlist
        global _app_instance
        _app_instance = self

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Input(placeholder="Enter a song title or URL...", id="song_input")
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        """Set up the table and hide the input when the app starts."""
        self.query_one("#song_input").display = False
        table = self.query_one(DataTable)
        table.add_columns("Title", "Duration")
        self.update_playlist_table()

    def format_duration(self, ms):
        """Formats milliseconds into MM:SS."""
        if not isinstance(ms, (int, float)):
            return "N/A"
        seconds = int(ms / 1000)
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_playlist_table(self):
        """Clears and refills the playlist table with current songs."""
        table = self.query_one(DataTable)
        table.clear()
        for song in self.playlist.queuedplaylist:
            # song is a dict {'title': '...', 'duration': ms}
            title = song.get('title', 'Unknown Title')
            duration_ms = song.get('duration')
            table.add_row(title, self.format_duration(duration_ms))

    async def on_ymp_app_playlist_updated(self, message: PlaylistUpdated) -> None:
        """Update the playlist table when a message is received."""
        self.update_playlist_table()

    def action_toggle_pause(self) -> None:
        """Toggle pause/play."""
        if self.playlist.songpaused:
            self.playlist.resumesong()
        else:
            self.playlist.pausesong()

    def action_next_song(self) -> None:
        """Play the next song."""
        self.playlist.nextsong()

    def action_prev_song(self) -> None:
        """Play the previous song."""
        self.playlist.previoussong()

    def action_shuffle(self) -> None:
        """Shuffle the playlist."""
        self.playlist.shuffleplaylist()

    def action_add_song(self) -> None:
        """Toggle the display of the song input."""
        song_input = self.query_one("#song_input")
        song_input.display = not song_input.display
        if song_input.display:
            song_input.focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle the submission of the input field."""
        song_query = event.value
        if song_query:
            self.playlist.addsong(song_query)

        event.input.clear()
        event.input.display = False

if __name__ == "__main__":
    from .playlistmanager import Playlist
    playlist = Playlist()
    playlist.queuedplaylist.extend([
        {'title': 'Song 1', 'duration': 185000},
        {'title': 'Song 2', 'duration': 245000},
    ])
    app = YmpApp(playlist=playlist)
    app.run()
