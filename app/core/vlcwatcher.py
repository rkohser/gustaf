import telnetlib
import threading


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
        return (
            self.send("get_time"),
            self.send("get_length"),
        )
