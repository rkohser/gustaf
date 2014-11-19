import tornado.websocket
import tornado.ioloop

from model import Episode
from core import VLCProcess


class PlayHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.vlc = VLCProcess()
        self.vlc.register_end_callback(self.on_play_end)
        self.vlc.register_progress_callback(self.on_play_progress)

    def open(self):
        print("Play webSocket opened")

    def on_message(self, episode_id):
        episode = Episode.get(id=episode_id)
        self.vlc.play(episode.path)

    def on_close(self):
        print("Play webSocket closed")

    def on_play_end(self):
        self.write_message("VLC Closed")
        print("VLC Closed")

    def on_play_progress(self, times):
        (current, total) = times
        self.write_message(str(int(float(current) / float(total) * 100.0)))
        print("VLC played : " + str(current) + "-" + str(total))

    def write_message(self, msg):
        tornado.ioloop.IOLoop.instance().add_callback(super().write_message, msg)