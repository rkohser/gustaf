from core.playstatemanager import PlayStateManager

__author__ = 'roland'

import tornado.websocket

from peewee import fn
from model import Season, Episode
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

            subquery = (Episode.select(
                Episode.season.alias('season_id'),
                Episode.episode_state.alias('state'),
                fn.Count(fn.distinct(Episode.episode_state)).alias('state_count'))
                        .join(Season)
                        .where(Season.show == msg.show_id)
                        .group_by(Season.id)).alias('sq')

            seasons = (Season.select(Season, Episode,
                                     subquery.c.state.alias('state'),
                                     subquery.c.state_count.alias('state_count'))
                       .join(Episode)
                       .join(subquery, on=(Season.id == subquery.c.season_id))
                       .where(Season.show == msg.show_id)
                       .order_by(Season.season_number.desc(), Episode.episode_number.asc())
                       .aggregate_rows())

            msg.data = self.render_string("episodes.html", seasons=seasons).decode()
            self.write_message(Message.to_json((msg,)))

        elif msg.message_type == MessageType.UPDATE_SEASON_STATE or msg.message_type == MessageType.UPDATE_EPISODE_STATE:

            message_list = PlayStateManager.handle_message(msg)
            self.write_message(Message.to_json(message_list))

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