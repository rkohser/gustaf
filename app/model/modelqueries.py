import datetime

from model import Show, Season, Episode, PlayState
from core import configurator
from peewee import fn


def query_shows_list_with_state():
    shows = (Show.select(Show.id, Show.name, fn.Count(fn.Distinct(Episode.episode_state)).alias('state_count'),
                         Episode.episode_state.alias('state'))
             .join(Season)
             .join(Episode)
             .order_by(Show.name)
             .group_by(Show.id)
             .dicts())

    res = list()
    for show in shows:
        if show['state_count'] > 1:
            show['state'] = PlayState.WATCHING
        del show['state_count']
        res.append(show)

    return res


def query_started_episodes():
    pass


def query_next_episodes():
    pass


def query_episodes_per_show_id(show_id=None):
    episodes = (Episode.select(Episode,
                               Season.season_number,
                               Show.name,
                               fn.REPLACE(fn.REPLACE(Episode.path, configurator.get()['settings']['search_path'], ''),
                                          '\\', '/').alias('url'))
                .join(Season)
                .join(Show)
                .dicts())

    if show_id:
        episodes = episodes.where(Season.show == show_id)

    return list(x for x in episodes)


def update_episode_status(data):
    episode = Episode.get(Episode.id == data['id'])

    episode.episode_state = PlayState.from_num(data['episode_state'][0])

    if "current_time" in data:
        episode.current_time = data['current_time']

    if "total_time" in data:
        episode.total_time = data['total_time']
        episode.last_watched = datetime.datetime.now()

    episode.save()
