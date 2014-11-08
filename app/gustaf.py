__author__ = 'roland'

import os
import sys

import tornado.ioloop
import tornado.web
import tornado.template

from model import ModelManager, Show


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

    ModelManager.init_model()
    ModelManager.update_model()

    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            items = [x.name.title() for x in Show.select(Show)]
            self.render("template.html", items=items)

    class ShowHandler(tornado.web.RequestHandler):
        def get(self):
            self.render("")

    class Application(tornado.web.Application):
        def __init__(self):
            handlers = [
                (r"/", MainHandler),
                (r"/show/", MainHandler),
                (r"/show/([^/]+)", ShowHandler)
            ]
            settings = {
                'debug': True,
                'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
                'static_path': os.path.join(os.path.dirname(__file__), 'static')
            }
            tornado.web.Application.__init__(self, handlers, **settings)

    application = Application()

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()