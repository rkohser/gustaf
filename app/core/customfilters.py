__author__ = 'roland'

from model import PlayState


def episode_progress(current_time, total_time, state=None):
    if state and (state is PlayState.NOT_WATCHED or PlayState.WATCHED):
        return 100.0
    else:
        return (current_time / total_time) * 100.0
