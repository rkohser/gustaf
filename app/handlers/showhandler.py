__author__ = 'roland'

import tornado.websocket
import tornado.ioloop
import json

from model import Show, Season, Episode, PlayState


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
        msg = json.loads(message)
        if msg['action'] == 'load_show':
            seasons = (Season.select(Season, Episode)
                       .join(Episode)
                       .where(Season.show == msg['show_id'])
                       .order_by(Season.season_number.desc(), Episode.episode_number.desc())
                       .aggregate_rows())

            msg['data'] = self.render_string("episodes.html", seasons=seasons).decode()
            self.write_message(json.dumps(msg))

        elif msg['action'] == 'update_episode_state':
            new_state = PlayState.from_text(msg['state']).next()
            msg['state'] = new_state.value
            self.write_message(json.dumps(msg))
            tornado.ioloop.IOLoop.instance().add_callback(self.set_episode_state, msg['episode_id'], new_state)

        elif msg['action'] == 'update_season_state':
            new_state = PlayState.from_text(msg['state']).next()
            msg['state'] = new_state.value
            self.write_message(json.dumps(msg))
            tornado.ioloop.IOLoop.instance().add_callback(self.set_season_state, msg['season_id'], new_state)

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