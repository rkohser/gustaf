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
        self.episode_id = None
        self.current = None
        self.total = None

    def open(self):
        print("Play webSocket opened")

    def on_message(self, episode_id):
        self.episode_id = episode_id
        episode = Episode.get(id=episode_id)
        self.vlc.play(episode.path, episode.current_time)

    def on_close(self):
        print("Play webSocket closed")

    def on_play_end(self):
        self.write_message("VLC Closed")
        print("VLC Closed")

    def on_play_progress(self, times):
        (self.current, self.total) = times
        tornado.ioloop.IOLoop.instance().add_callback(self.do_in_ioloop)

    def do_in_ioloop(self):
        # update db
        Episode.update(current_time=float(self.current)).where(Episode.id == self.episode_id).execute()
        # update progress bar
        self.write_message(str(int(float(self.current) / float(self.total) * 100.0)))
        # print to console
        print("VLC played : " + str(self.current) + "-" + str(self.total))