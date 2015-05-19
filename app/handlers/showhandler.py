from core.playstatemanager import PlayStateManager

__author__ = 'roland'

import tornado.websocket

from model import Season, Episode
from core import Message, MessageType, parse_message
from core import register_handler
from core import get_subs
from core import Jinja2Renderer


class ShowHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.renderer = Jinja2Renderer(self.settings)

    def initialize(self, name):
        register_handler(name, self)

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

            season_infos = (Season.select(Season.id, Season.season_number)
                            .where(Season.show == msg.show_id)
                            .tuples())

            seasons = list()
            if season_infos.exists():
                for season_id, season_number in season_infos:
                    seasons.append((season_number, (Episode.select()
                                                    .where(Episode.season == season_id)
                                                    .dicts())))

            msg.data = self.renderer.render_string("episodes.html", show_name=msg.show_name, seasons=seasons,
                                                   languages={'eng', 'fra'})
            self.write_message(Message.to_json((msg,)))

        elif msg.message_type == MessageType.UPDATE_EPISODE_STATE:

            old_state, = (Episode.select(Episode.episode_state).where(Episode.id == msg.episode_id).tuples()).get()
            msg.state = old_state
            message_list = PlayStateManager.handle_message(msg)
            self.write_message(Message.to_json(message_list))

        elif msg.message_type == MessageType.UPDATE_SEASON_STATE:

            message_list = PlayStateManager.handle_message(msg)
            self.write_message(Message.to_json(message_list))

        elif msg.message_type == MessageType.GET_SUBTITLES:

            episode = Episode.get(Episode.id == msg.episode_id)
            new_sub = get_subs(episode.path, {msg.lang})
            if new_sub:
                msg.result = "success"
                Episode.update(subtitles=episode.subtitles.union(new_sub)).where(
                    Episode.id == msg.episode_id).execute()
            else:
                msg.result = "danger"

            self.write_message(Message.to_json((msg,)))

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