__author__ = 'roland'

import tornado.web

from peewee import fn
from model import Show, Season, Episode, PlayState


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        shows = (Show.select(Show.id, Show.name, fn.Count(fn.Distinct(Episode.episode_state)).alias('state_count'),
                             Episode.episode_state.alias('state'))
                 .join(Season)
                 .join(Episode)
                 .order_by(Show.name)
                 .group_by(Show.id)
                 .dicts())

        # Build dashboard info
        watching_epsiodes = (Episode.select(Show.name.alias('show_name'),
                                            Season.season_number.alias('season_number'),
                                            Episode)
                             .join(Season)
                             .join(Show)
                             .where(Episode.episode_state == PlayState.WATCHING)
                             .order_by(Episode.last_watched.desc())
                             .dicts())

        self.render("shows.html", shows=shows, languages={'eng', 'fra'}, watching_episodes=watching_epsiodes)
