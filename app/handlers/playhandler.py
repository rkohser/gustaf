import tornado.websocket
import tornado.ioloop
import json

from model import Episode, PlayState
from core import VLCProcess


class PlayHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.vlc = VLCProcess()
        self.vlc.register_end_callback(self.on_play_end)
        self.vlc.register_progress_callback(self.on_play_progress)
        self.episode_id = None

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
        tornado.ioloop.IOLoop.instance().add_callback(self.do_in_ioloop, status)

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

    def do_in_ioloop(self, status):
        # update gustaf status
        if status['state'] == 'playing':
            status["progress"] = int(float(status["get_time"]) / float(status["get_length"]) * 100.0)
            # is it finished ?
            if (status["get_length"] - status["get_time"]) < 180:
                Episode.update(current_time=0.0, state=PlayState.WATCHED).where(Episode.id == self.episode_id).execute()
            else:
                Episode.update(current_time=float(status["get_time"])).where(Episode.id == self.episode_id).execute()
        self.write_message(json.dumps(status))

