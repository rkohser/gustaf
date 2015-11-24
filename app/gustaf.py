import sys

import os
import tornado.ioloop
import tornado.web
import tornado.template
from model import ModelManager
from handlers import MainHandler, ShowHandler, PlayHandler, ShowListHandler, EpisodeHandler
from core import configurator


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

    configurator.init('settings.json')

    ModelManager.init_model()
    ModelManager.update_model()
    ModelManager.update_subtitles()

    class Application(tornado.web.Application):

        def __init__(self):
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            handlers = [
                (r"/show", ShowHandler, {'name': 'show'}),
                (r"/play", PlayHandler, {'name': 'play'}),
                (r"/shows", ShowListHandler),
                (r"/episodes/([^/]*)", EpisodeHandler),
                (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "app/index.html"})
            ]

            settings = {
                'debug': True,
                'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            }
            tornado.web.Application.__init__(self, handlers, **settings)

    application = Application()

    application.listen(8888)
    print("Starting tornado loop ...")
    tornado.ioloop.IOLoop.instance().start()
