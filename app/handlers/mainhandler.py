__author__ = 'roland'

import tornado.web

from model import Show, Season


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # shows = dict()
        # for show in Show.select(Show):
        # shows[show.name] = [x.number for x in Season.select(Season).where(show=show).join(Show)]

        shows = (Show.select(Show, Season)
                 .join(Season)
                 .order_by(Show.name)
                 .aggregate_rows())

        self.render("template.html", shows=shows, episodes=[])
