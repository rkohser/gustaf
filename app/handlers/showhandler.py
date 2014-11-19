__author__ = 'roland'

import tornado.websocket

from model import Season, Episode


class ShowHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Show webSocket opened")

    def on_message(self, season_id):
        episodes = (Episode.select(Season, Episode)
                    .join(Season)
                    .where(Season.id == season_id))

        title = episodes[0].season.show.name.title() + " - Season " + episodes[0].season.number

        self.write_message(self.render_string("episodes.html", episodes=episodes, title=title))

    def on_close(self):
        print("Show webSocket closed")