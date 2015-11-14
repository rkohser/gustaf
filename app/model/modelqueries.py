from model import Show, Season, Episode, PlayState
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


def query_episodes_per_show_id():
    pass
