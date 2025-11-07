import os
import time
from pydub import AudioSegment
import simpleaudio

# A mock play object for environments without audio hardware
class MockPlayObject:
    def __init__(self, duration_seconds=5):
        self._start_time = time.time()
        self._duration = duration_seconds
        self.stopped = False

    def is_playing(self):
        if self.stopped:
            return False
        return (time.time() - self._start_time) < self._duration

    def stop(self):
        self.stopped = True

def has_audio_device():
    """Check for the presence of ALSA audio devices."""
    try:
        if any(os.scandir('/dev/snd/')):
            return True
    except (FileNotFoundError, NotADirectoryError):
        pass
    return False

def genmusic(name, resumetime):
    """Generates a simpleaudio object for playback or a mock object if no audio device is found."""
    if not has_audio_device():
        print("[Notice] No audio device detected. Simulating playback for 5 seconds.")
        t0 = time.time()
        playobj = MockPlayObject(duration_seconds=5)
        return playobj, t0

    try:
        sound = AudioSegment.from_file(name)
        sound = sound[resumetime:]
        playback = simpleaudio.WaveObject(
            sound.raw_data,
            num_channels=sound.channels,
            bytes_per_sample=sound.sample_width,
            sample_rate=sound.frame_rate
        )
        t0 = time.time()
        playobj = playback.play()
        return playobj, t0
    except Exception:
        print("[Warning] Audio playback failed unexpectedly. Simulating playback.")
        t0 = time.time()
        playobj = MockPlayObject(duration_seconds=5)
        return playobj, t0

def pausemusic(playobj):
    """Pauses the music playback."""
    t1 = time.time()
    playobj.stop()
    return t1

def wait():
    """Waits for a short period."""
    time.sleep(5)
