from core.playstatemanager import PlayStateManager

__author__ = 'roland'

import tornado.websocket

from model import Season, Episode
from core import MessageType, parse_message


class ShowHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Show webSocket opened")

    def on_message(self, message):
        """
        Handles message from the websocket
        :param message:
        {
            "action": "load_show"|"load_season"|"update_episode_state"|"update_season_state"
            "episode_id": int id
            "season_id": int id
            "show_id": int id
            "state": json_dump from a model state enum
        }
        :return:
        """

        msg = parse_message(message)
        if msg.message_type == MessageType.LOAD_SHOW:
            seasons = (Season.select(Season, Episode)
                       .join(Episode)
                       .where(Season.show == msg.show_id)
                       .order_by(Season.season_number, Episode.episode_number)
                       .aggregate_rows())
            msg.data = self.render_string("episodes.html", seasons=seasons).decode()
            self.write_message(msg.to_json())

        elif msg.message_type == MessageType.UPDATE_SEASON_STATE or msg.message_type == MessageType.UPDATE_EPISODE_STATE:
            self.write_message(PlayStateManager.handle_message(msg).to_json())

    def write_message(self, message):
        """
        Sends a message to the websocket
        :param message:
        {
            "action": "load_show"|"load_season"|"update_episode_state"|"update_season_state"
            "episode_id": int id
            "season_id": int id
            "show_id": int id
            "state": json_dump from a model state enum
            "data": ex:html content
        }
        :return:
        """
        super().write_message(message)

    def on_close(self):
        print("Show webSocket closed")