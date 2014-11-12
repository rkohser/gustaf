__author__ = 'roland'

import tornado.websocket

from model import Season, Episode


class ShowHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, season_id):
        episodes = (Episode.select(Season, Episode)
                    .join(Season)
                    .where(Season.id == season_id))

        self.write_message(self.render_string("episodes.html", episodes=episodes))

    def on_close(self):
        print("WebSocket closed")