import tornado.websocket
import tornado.ioloop
import json

from model import Episode, PlayState
from core import VLCProcess, VLCState
from core import register_handler, get_handler
from core import PlayStateManager
from core import Message


class PlayHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.vlc = VLCProcess()
        self.vlc.register_end_callback(self.on_play_end)
        self.vlc.register_progress_callback(self.on_play_progress)
        self.episode_id = None
        self.episode_state = None
        self.last_current_time = None
        self.last_total_time = None
        self.old_state = PlayState.NOT_WATCHED

    def initialize(self, name):
        register_handler(name, self)

    def open(self):
        print("Play webSocket opened")

    def on_message(self, episode_id):
        """
        Handles message from the websocket
        :param episode_id:
        :return:
        """
        self.episode_id = episode_id
        episode = Episode.get(id=episode_id)
        self.vlc.play(episode.path, episode.current_time)

    def on_close(self):
        print("Play webSocket closed")

    def on_play_end(self):
        self.write_message(json.dumps({'state': 'stopped'}))

    def on_play_progress(self, status):
        state = status.deduce_episode_state()
        if self.old_state != state:
            msg_list = PlayStateManager.update_episode(self.episode_id, self.old_state, state, status.current_time)
            get_handler('show').write_message(Message.to_json(msg_list))

            self.old_state = state

        self.write_message(status.to_json())

    def write_message(self, message):
        """
        Sends a message to the websocket
        :param message:
        {
            "get_time": int seconds,
            "file": string,
            "get_length": int seconds,
            "state": "playing"|"stopped"|"paused",
            "progress": int percents
        }
        :return:
        """
        super().write_message(message)

