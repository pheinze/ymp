# YMP - Your Music Player

YMP is a powerful, command-line music player for YouTube. It allows you to play single songs, entire playlists, and manage your queue with ease, all from the comfort of your terminal.

## Features

- **Play YouTube Playlists**: Simply provide a YouTube playlist URL to start listening.
- **Play Single Songs**: Search for and play any song from YouTube.
- **Queue Management**: Add songs to the queue, remove them, and shuffle your playlist.
- **Playback Control**: Play, pause, skip to the next song, or go back to the previous one.
- **Save and Load Playlists**: Save your current queue as a playlist and load it back later.
- **Repeat Modes**: Set repeat mode to off, repeat the entire playlist, or repeat the current song.
- **Seek Functionality**: Jump forward or backward in the current song.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/pheinze/ymp.git
    cd ymp
    ```

2.  **Install the dependencies:**

    Make sure you have `pip` and the necessary system dependencies installed. On Debian-based systems, you can install the required audio library with:

    ```bash
    sudo apt-get update
    sudo apt-get install -y libasound2-dev
    ```

    Then, install the Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Install the application:**

    ```bash
    pip install .
    ```

## Usage

You can start `ymp` with various command-line arguments to immediately start playing music.

-   **Play a YouTube playlist:**

    ```bash
    ymp -y <YOUTUBE_PLAYLIST_URL>
    ```

-   **Play one or more songs:**

    ```bash
    ymp -p "Song Name 1" "Song Name 2"
    ```

-   **Load a saved playlist:**

    ```bash
    ymp -l <PLAYLIST_NAME>
    ```

### Interactive Commands

Once `ymp` is running, you can use the following commands in the terminal:

-   `youtube`: Play a YouTube playlist.
-   `play`: Resume the current song.
-   `pause`: Pause the current song.
-   `next`: Play the next song in the queue.
-   `back`: Play the previous song.
-   `shuffle`: Shuffle the current queue.
-   `rm`: Remove the last song from the queue.
-   `repeat <off|all|song>`: Set the repeat mode.
-   `seek <SECONDS>`: Seek forward or backward in the current song (e.g., `seek 10` or `seek -10`).
-   `save`: Save the current queue as a playlist.
-   `load`: Load a previously saved playlist.
-   `download`: Download the currently playing song.
-   `commands`: Display a list of all available commands.
-   `exit`: Exit the application.

Any other input will be treated as a search query for a song to be added to the queue.

## License

This project is licensed under the MIT License.
