import telnetlib
import re


class WrongPasswordError(Exception):
    pass


class VLCWatcher():
    def __init__(self, server="localhost", port=4212, password="admin", timeout=5):
        self.server = server
        self.port = port
        self.password = password
        self.timeout = timeout
        self.telnet = None
        self.current_time = 0
        self.total_time = 0

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
        if status["state"] != "stopped":
            status["get_time"] = int(self.send("get_time"))
            status["get_length"] = int(self.send("get_length"))
        return status

    def parse_status(self, status_str):
        status = dict()
        try:
            status["state"] = self.status_re.search(status_str).group("state")
        except:
            status["state"] = "Error while querying state"
        else:
            if status["state"] == "playing" or status["state"] == "paused":
                try:
                    status["file"] = self.current_file_re.search(status_str).group("file")
                except:
                    status["file"] = "Error while querying current file"
        return status
