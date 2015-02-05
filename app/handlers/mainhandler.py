__author__ = 'roland'

import tornado.web

from peewee import fn
from model import Show, Season, Episode


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        shows = (Show.select(Show.id, Show.name, fn.Count(fn.Distinct(Episode.episode_state)).alias('state_count'),
                             Episode.episode_state.alias('state'))
                 .join(Season)
                 .join(Episode)
                 .order_by(Show.name)
                 .group_by(Show.id)
                 .dicts())

        self.render("shows.html", shows=shows)
