__author__ = 'roland'

import tornado.websocket
import tornado.ioloop

from model import Season, Episode, PlayState
from core import Message, MessageType, parse_message


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

        elif msg.message_type == MessageType.UPDATE_SEASON_STATE:
            msg.state = msg.state.next()
            self.write_message(msg.to_json())
            tornado.ioloop.IOLoop.instance().add_callback(self.set_episode_state, msg.episode_id, msg.state)

        elif msg.message_type == MessageType.UPDATE_EPISODE_STATE:
            msg.state = msg.state.next()
            self.write_message(msg.to_json())
            tornado.ioloop.IOLoop.instance().add_callback(self.set_season_state, msg.season_id, msg.state)

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

    def set_episode_state(self, episode_id, state):
        Episode.update(episode_state=state).where(Episode.id == episode_id).execute()

    def set_season_state(self, season_id, state):
        Season.update(season_state=state).where(Season.id == season_id).execute()