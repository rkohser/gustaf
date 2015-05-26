__author__ = 'roland'

from model import PlayState, Episode
import sys


def episode_progress(episode):
    if episode.episode_state and (episode.episode_state is PlayState.NOT_WATCHED or PlayState.WATCHED):
        return 100.0
    else:
        return (episode.current_time / episode.total_time) * 100.0


def show_state(show):
    season_states = {season_state(season) for season in show.seasons}
    if len(season_states) is 1:
        return season_states.pop()
    else:
        return PlayState.WATCHING


def season_state(season):
    episode_states = {episode.episode_state for episode in season.episodes}
    if len(episode_states) is 1:
        return episode_states.pop()
    else:
        return PlayState.WATCHING


def started_episodes(shows):
    started = list()
    for show in (watching_show for watching_show in shows if show_state(watching_show) is PlayState.WATCHING):
        for season in (watching_season for watching_season in show.seasons if
                       season_state(watching_season) is PlayState.WATCHING):
            for episode in season.episodes:
                if episode.episode_state is PlayState.WATCHING:
                    started.append((show.name, season.season_number, episode))

    return started


def next_episodes(shows):
    next = list()
    for show in shows:
        for season in (watching_season for watching_season in show.seasons if
                       season_state(watching_season) is PlayState.WATCHING):
            next_episode = None
            episode_num = sys.maxsize
            for episode in season.episodes:
                if episode.episode_state is PlayState.NOT_WATCHED and episode.episode_number < episode_num:
                    episode_num = episode.episode_number
                    next_episode = episode

            if next_episode:
                next.append((show.name, season.season_number, next_episode))

    return next
