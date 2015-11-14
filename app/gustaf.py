import sys

import os
import tornado.ioloop
import tornado.web
import tornado.template
from model import ModelManager
from handlers import MainHandler, ShowHandler, PlayHandler, ShowListHandler
from core import configurator


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

    configurator.init('settings.json')

    ModelManager.init_model()
    ModelManager.update_model()
    ModelManager.update_subtitles()

    class Application(tornado.web.Application):

        def __init__(self):
            handlers = [
                (r"/", MainHandler),
                (r"/show", ShowHandler, {'name': 'show'}),
                (r"/play", PlayHandler, {'name': 'play'}),
                (r"/shows", ShowListHandler)
            ]

            settings = {
                'debug': True,
                'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
                'static_path': os.path.join(os.path.dirname(__file__), 'static')
            }
            tornado.web.Application.__init__(self, handlers, **settings)

    application = Application()

    application.listen(8888)
    print("Starting tornado loop ...")
    tornado.ioloop.IOLoop.instance().start()