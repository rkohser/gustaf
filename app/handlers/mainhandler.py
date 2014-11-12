__author__ = 'roland'

import tornado.web

from model import Show, Season


class MainHandler(tornado.web.RequestHandler):
    def get(self):

        shows = (Show.select(Show, Season)
                 .join(Season)
                 .order_by(Show.name)
                 .aggregate_rows())

        self.render("shows.html", shows=shows)
