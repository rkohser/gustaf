__author__ = 'roland'

import tornado.web

from model import Season, Show


class ShowHandler(tornado.web.RequestHandler):
    def get(self, show_id):
        shows = [x.name.title() for x in Show.select(Show)]
        seasons = [x.number for x in Season.select(Show, Season).join(Show).where(Show.id == show_id)]
        self.render("template.html", shows=shows, seasons=seasons, episodes=[])
