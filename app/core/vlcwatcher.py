import telnetlib
import json
import re
from enum import Enum, unique
from model import PlayState
from core.helpers import ModelEncoder


class WrongPasswordError(Exception):
    pass


@unique
class VLCState(Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"

    def __init__(self, text):
        self.text = text

    @classmethod
    def from_text(cls, text):
        dic = {member.text: member for name, member in cls.__members__.items()}
        return dic[text]


class VLCStatus:
    def __init__(self, state):
        self.state = VLCState.from_text(state)
        self.file = None
        self._current_time = None
        self._total_time = None
        self.progress = None

    @property
    def current_time(self):
        return self._current_time

    @current_time.setter
    def current_time(self, value):
        self._current_time = float(value)

    @property
    def total_time(self):
        return self._total_time

    @total_time.setter
    def total_time(self, value):
        self._total_time = float(value)

    def update_progress(self):
        self.progress = int(self._current_time / self._total_time * 100.0)

    def deduce_episode_state(self):
        try:
            if self.current_time < 180:
                return PlayState.NOT_WATCHED
            elif (self.total_time - self.current_time) < 180:
                return PlayState.WATCHED
            else:
                return PlayState.WATCHING
        except:
            return PlayState.NOT_WATCHED

    def to_json(self):
        # transform into dict list
        return json.dumps(self.__dict__, cls=ModelEncoder)


class VLCWatcher:
    def __init__(self, server="localhost", port=4212, password="admin", timeout=5):
        self.server = server
        self.port = port
        self.password = password
        self.timeout = timeout
        self.telnet = None

        self.status_re = re.compile(r'\( state (?P<state>\w+) \)')
        self.current_file_re = re.compile(r"\( new input: (?P<file>.+) \)")

    def connect(self):
        assert self.telnet is None, "connect() called twice"

        self.telnet = telnetlib.Telnet()
        self.telnet.open(self.server, self.port, self.timeout)

        # Login
        self.telnet.read_until(b"Password: ")
        self.telnet.write(self.password.encode())
        self.telnet.write(b"\n")

        # Password correct?
        result = self.telnet.expect([
            b"Password: ",
            b">"
        ])
        if b"Password" in result[2]:
            raise WrongPasswordError()

    def disconnect(self):
        self.telnet.close()
        self.telnet = None

    def send(self, line):
        self.telnet.write(line.encode() + b"\n")
        return self.telnet.read_until(b">").decode()[1:-3]

    def watch(self):
        # 1. status and current file
        status = self.parse_status(self.send("status"))
        # 2. if playing, get time
        if status.state != VLCState.STOPPED:
            status.current_time = self.send("get_time")
            status.total_time = self.send("get_length")
            status.update_progress()
        return status

    def parse_status(self, status_str):

        status = None
        try:
            status = VLCStatus(self.status_re.search(status_str).group("state"))
        except:
            pass
        else:
            if status.state == VLCState.PLAYING or status.state == VLCState.PAUSED:
                try:
                    status.file = self.current_file_re.search(status_str).group("file")
                except:
                    pass
        return status
