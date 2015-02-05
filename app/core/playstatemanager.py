__author__ = 'roland'

import tornado.ioloop

from core import Message, MessageType
from model import Season, Episode


class PlayStateManager:
    def __init__(self):
        pass

    @staticmethod
    def handle_message(msg):

        assert isinstance(msg, Message)
        if msg.message_type == MessageType.UPDATE_EPISODE_STATE:
            # toggle state
            msg.state = msg.state.next()
            msg.season_id = 32

            # query other episodes states
            states = (Episode.select(Episode.episode_state)
                      .where((Episode.season == msg.season_id) & (Episode.id != msg.episode_id))
                      .group_by(Episode.episode_state))

            states_list = list(states)
            if len(states_list) == 1 and states_list[0].episode_state == msg.state:
                print('toggle')

            # commit DB changes
            tornado.ioloop.IOLoop.instance().add_callback(PlayStateManager.set_episode_state, msg.episode_id, msg.state)
            return msg

        elif msg.message_type == MessageType.UPDATE_SEASON_STATE:
            msg.state = msg.state.next()
            tornado.ioloop.IOLoop.instance().add_callback(PlayStateManager.set_season_state, msg.season_id, msg.state)
            return msg

    @staticmethod
    def set_episode_state(episode_id, state):
        Episode.update(episode_state=state).where(Episode.id == episode_id).execute()

    @staticmethod
    def set_season_state(season_id, state):
        Season.update(season_state=state).where(Season.id == season_id).execute()
