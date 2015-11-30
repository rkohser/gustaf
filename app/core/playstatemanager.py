import datetime

import tornado.ioloop
from peewee import fn

from core import Message, MessageType
from model import Season, Episode, PlayState


class PlayStateManager:
    @staticmethod
    def update_episode(episode_id, old_episode_state, new_state, current_time, total_time):

        msg_list = list()

        # update episode state label
        msg_list.append(Message(MessageType.UPDATE_EPISODE_STATE, episode_id=episode_id, state=new_state))

        # cascade season state if actual state change
        if old_episode_state != new_state:
            msg_list.extend(PlayStateManager.cascade_season_state(episode_id, old_episode_state, new_state))

        # commit db changes
        tornado.ioloop.IOLoop.instance().add_callback(
            PlayStateManager.set_episode_state, episode_id, new_state, current_time, total_time)

        return msg_list

    @staticmethod
    def handle_message(msg):
        assert isinstance(msg, Message)
        msg_list = list()
        if msg.message_type == MessageType.UPDATE_EPISODE_STATE:
            # toggle state
            old_episode_state = msg.state
            msg.state = old_episode_state.next()

            # query other states if cascading is needed
            msg_list.extend(PlayStateManager.cascade_season_state(msg.episode_id, old_episode_state, msg.state))

            # commit DB changes
            tornado.ioloop.IOLoop.instance().add_callback(PlayStateManager.set_episode_state, msg.episode_id, msg.state)
            msg_list.append(msg)

        elif msg.message_type == MessageType.UPDATE_SEASON_STATE:
            # toggle state
            old_season_state = msg.state
            msg.state = old_season_state.next()

            # toggle episodes states in browser
            episode_ids = Episode.select(Episode.id).where(Episode.season == msg.season_id).tuples()
            for episode_id, in episode_ids:
                msg_list.append(Message(MessageType.UPDATE_EPISODE_STATE, episode_id=episode_id, state=msg.state))

            # cascade to show state
            msg_list.extend(PlayStateManager.cascade_show_state(msg.season_id, old_season_state, msg.state))

            # commit DB changes
            tornado.ioloop.IOLoop.instance().add_callback(PlayStateManager.set_season_state, msg.season_id, msg.state)
            msg_list.append(msg)

        return msg_list

    @staticmethod
    def set_episode_state(episode_id, state, current_time=0.0, total_time=0.0):
        # store surrent time onlw if watching
        if state != PlayState.WATCHING:
            current_time = 0.0

        # store last watched datetime only for watched and watching
        if state != PlayState.NOT_WATCHED:
            last_watched = datetime.datetime.now()
        else:
            last_watched = None
        Episode.update(episode_state=state, current_time=current_time, total_time=total_time,
                       last_watched=last_watched).where(
            Episode.id == episode_id).execute()

    @staticmethod
    def set_season_state(season_id, state):
        Episode.update(episode_state=state, current_time=0.0).where(Episode.season == season_id).execute()

    @staticmethod
    def process_parent_state(old_child_state, new_child_state, other_children_state, other_children_state_count):

        # process old parent state
        if other_children_state_count == 1 and other_children_state == old_child_state:
            old_parent_state = old_child_state
        else:
            old_parent_state = PlayState.WATCHING

        # process new parent state
        if other_children_state_count == 1 and other_children_state == new_child_state:
            new_parent_state = new_child_state
        else:
            new_parent_state = PlayState.WATCHING

        return old_parent_state, new_parent_state

    @staticmethod
    def cascade_season_state(episode_id, old_episode_state, new_episode_state):

        msg_list = list()

        # subquery to get season id
        season_id, = (Episode.select(Episode.season)
                      .where(Episode.id == episode_id)
                      .tuples()).get()

        # query to get other episodes sttaes
        other_states_query = (Episode.select(Episode.episode_state.alias('other_state'),
                                             fn.Count(fn.Distinct(Episode.episode_state)).alias('state_count'))
                              .where(Episode.id != episode_id)
                              .group_by(Episode.season)
                              .having(Episode.season == season_id)
                              .tuples())

        try:
            other_episodes_state, other_episodes_state_count = other_states_query.get()
        except Episode.DoesNotExist:
            # it is the only episode in the season, so changing episode state changes season state to the same
            msg_list.append(Message(MessageType.UPDATE_SEASON_STATE, season_id=season_id, state=new_episode_state))
            # season state changed, cascade if needed
            msg_list.extend(PlayStateManager.cascade_show_state(season_id, old_episode_state, new_episode_state))
        else:
            # dependant on other episodes
            old_season_state, new_season_state = PlayStateManager.process_parent_state(old_episode_state,
                                                                                       new_episode_state,
                                                                                       other_episodes_state,
                                                                                       other_episodes_state_count)
            if old_season_state != new_season_state:
                msg_list.append(Message(MessageType.UPDATE_SEASON_STATE, season_id=season_id, state=new_season_state))
                # season state changed, cascade if needed
                msg_list.extend(PlayStateManager.cascade_show_state(season_id, old_season_state, new_season_state))

        return msg_list

    @staticmethod
    def cascade_show_state(season_id, old_season_state, new_season_state):

        msg_list = list()

        # subquery to get season id
        show_id, = (Season.select(Season.show)
                    .where(Season.id == season_id)
                    .tuples()).get()

        # query to get other episodes sttaes
        other_states_query = (Season.select(Episode.episode_state.alias('other_state'),
                                            fn.Count(fn.Distinct(Episode.episode_state)).alias('state_count'))
                              .join(Episode)
                              .where(Season.id != season_id)
                              .group_by(Season.show)
                              .having(Season.show == show_id)
                              .tuples())

        try:
            other_seasons_state, other_seasons_state_count = other_states_query.get()
        except Season.DoesNotExist:
            # it is the only season in the show, so changing season state changes show state to the same
            msg_list.append(Message(MessageType.UPDATE_SHOW_STATE, show_id=show_id, state=new_season_state))
        else:
            # dependant on other seasons
            old_show_state, new_show_state = PlayStateManager.process_parent_state(old_season_state, new_season_state,
                                                                                   other_seasons_state,
                                                                                   other_seasons_state_count)
            if old_show_state != new_show_state:
                msg_season = Message(MessageType.UPDATE_SHOW_STATE, show_id=show_id, state=new_show_state)
                msg_list.append(msg_season)

        return msg_list
