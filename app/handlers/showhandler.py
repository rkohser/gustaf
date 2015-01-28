__author__ = 'roland'

import tornado.websocket
import json

from model import Season, Episode


class ShowHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Show webSocket opened")

    def on_message(self, message):
        """
        Handles message from the websocket
        :param message:
        {
            "action": "load_season"|"update_episode_state"|"update_season_state"
            "episode_id": int id
            "season_id": int id
            "state": json_dump from a model state enum
        }
        :return:
        """
        msg = json.loads(message)
        if msg['action'] == 'load_season':
            episodes = (Episode.select(Season, Episode)
                        .join(Season)
                        .where(Season.id == msg['season_id']))

            title = episodes[0].season.show.name.title() + " - Season " + str(episodes[0].season.number)

            msg['data'] = self.render_string("episodes.html", episodes=episodes, title=title).decode()
            self.write_message(json.dumps(msg))

    def write_message(self, message):
        """
        Sends a message to the websocket
        :param message:
        {
            "action": "load_season"|"update_episode_state"|"update_season_state"
            "episode_id": int id
            "season_id": int id
            "state": json_dump from a model state enum
            "data": ex:html content
        }
        :return:
        """
        super().write_message(message)

    def on_close(self):
        print("Show webSocket closed")