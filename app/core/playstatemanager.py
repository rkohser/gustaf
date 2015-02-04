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
            msg.state = msg.state.next()
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

