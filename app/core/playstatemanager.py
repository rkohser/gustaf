__author__ = 'roland'

import tornado.ioloop
from peewee import fn

from core import Message, MessageType
from model import Episode, PlayState


class PlayStateManager:
    def __init__(self):
        pass

    @staticmethod
    def handle_message(msg):
        assert isinstance(msg, Message)
        message_list = list()
        if msg.message_type == MessageType.UPDATE_EPISODE_STATE:
            # toggle state
            old_episode_state = msg.state
            msg.state = old_episode_state.next()

            # query other episodes states
            subquery = (Episode.select(Episode.season)
                        .where(Episode.id == msg.episode_id))

            other_states_query = (Episode.select(Episode.season.alias('season_id'),
                                                 Episode.episode_state.alias('other_state'),
                                                 fn.Count(fn.Distinct(Episode.episode_state)).alias('state_count'))
                                  .where(Episode.id != msg.episode_id)
                                  .group_by(Episode.season)
                                  .having(Episode.season.in_(subquery))
                                  .tuples())

            season_id, other_episodes_state, other_episodes_state_count = other_states_query.get()
            changed, new_season_state = PlayStateManager.process_season_state(old_episode_state, msg.state,
                                                                              other_episodes_state,
                                                                              other_episodes_state_count)
            if changed:
                msg_season = Message(MessageType.UPDATE_SEASON_STATE, season_id=season_id, state=new_season_state)
                message_list.append(msg_season)

            # commit DB changes
            tornado.ioloop.IOLoop.instance().add_callback(PlayStateManager.set_episode_state, msg.episode_id, msg.state)
            message_list.append(msg)

        elif msg.message_type == MessageType.UPDATE_SEASON_STATE:
            msg.state = msg.state.next()
            # tornado.ioloop.IOLoop.instance().add_callback(PlayStateManager.set_season_state, msg.season_id, msg.state)
            message_list.append(msg)

        return message_list

    @staticmethod
    def set_episode_state(episode_id, state):
        Episode.update(episode_state=state).where(Episode.id == episode_id).execute()

    @staticmethod
    def set_season_state(season_id, state):
        pass
        # Season.update(season_state=state).where(Season.id == season_id).execute()

    @staticmethod
    def process_season_state(old_episode_state, new_episode_state, other_episodes_state, other_episodes_state_count):

        # process old season state
        if other_episodes_state_count == 1 and other_episodes_state == old_episode_state:
            old_season_state = old_episode_state
        else:
            old_season_state = PlayState.WATCHING

        # process new season state
        if other_episodes_state_count == 1 and other_episodes_state == new_episode_state:
            new_season_state = new_episode_state
        else:
            new_season_state = PlayState.WATCHING

        return old_season_state != new_season_state, new_season_state
