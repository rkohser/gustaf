import subprocess
import threading
import time

from core.vlcwatcher import VLCWatcher


class VLCProcess:
    def __init__(self):
        super().__init__()

        self.process = None
        self.watcher = VLCWatcher()
        self.watching_process = None

        self.vlc_path = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
        self.vlc_options = [
            "--one-instance",
            "--sub-language",
            "fra",
            "--extraintf",
            "telnet",
            "--telnet-password",
            "admin"
        ]

        self.end_callback = None
        self.progress_callback = None

        self.stop = threading.Event()

    def register_end_callback(self, end_callback):
        """
        Registers end callback, called when VLC has been closed
        :param end_callback: function without any parameters
        """
        self.end_callback = end_callback

    def register_progress_callback(self, progress_callback):
        """
        Registers the progress callback, called periodically to inform the progress of the stream
        :param progress_callback: function taking current time and total time
        """
        self.progress_callback = progress_callback

    def play(self, episode, start_time=0.0):

        self.vlc_options.append("--start-time=" + str(start_time))

        # Prepapre player
        command = [self.vlc_path] + self.vlc_options + [episode]
        self.process = threading.Thread(target=self._play, args=(command,)).start()

        # Prepare watcher
        self.stop.clear()
        self.watcher.connect()
        self.watching_process = threading.Thread(target=self._watch).start()

    def _play(self, command):
        subprocess.call(command)
        self.stop.set()
        self.end_callback()
        self.process = None
        self.watcher.disconnect()
        self.watching_process = None

    def _watch(self):

        while not self.stop.is_set():
            time.sleep(5)
            try:
                self.progress_callback(self.watcher.watch())
            except:
                pass
