import datetime

from model import Show, Season, Episode, PlayState
from core import configurator
from peewee import fn


def episode_request():
    return (Episode.select(Episode,
                           Season.season_number,
                           Show.name.alias('show_name'),
                           Show.id.alias('show_id'),
                           fn.REPLACE(fn.REPLACE(Episode.path, configurator.get()['settings']['search_path'], ''),
                                      '\\', '/').alias('url'))
            .join(Season)
            .join(Show)
            .dicts())


def to_list(datalist):
    return list(x for x in datalist)


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


def query_added_episodes():
    return to_list(episode_request()
                   .where(
        Episode.added_time.between(datetime.datetime.now() + datetime.timedelta(weeks=-1), datetime.datetime.now()),
        Episode.episode_state==PlayState.NOT_WATCHED))


def query_started_episodes():
    return to_list(episode_request()
                   .where(Episode.episode_state == PlayState.WATCHING))


def query_next_episodes():
    return to_list(episode_request()
                   .where(Episode.episode_state == PlayState.NOT_WATCHED)
                   .group_by(Show.id)
                   .having(Episode.episode_number != 1)
                   .order_by(fn.Min(Episode.episode_number)))


def query_episodes_per_show_id(show_id=None):
    episodes = episode_request()

    if show_id:
        episodes = episodes.where(Season.show == show_id)

    return to_list(episodes)


def update_episode_status(data):
    episode = Episode.get(Episode.id == data['id'])

    episode.episode_state = PlayState.from_num(data['episode_state'][0])

    if "current_time" in data:
        episode.current_time = data['current_time']
    else:
        episode.current_time = 0

    if "total_time" in data:
        episode.total_time = data['total_time']
        episode.last_watched = datetime.datetime.now()

    episode.save()
