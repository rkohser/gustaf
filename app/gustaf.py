__author__ = 'roland'

import sys

import os
import tornado.ioloop
import tornado.web
import tornado.template
from model import ModelManager
from handlers import MainHandler, ShowHandler, PlayHandler


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

    ModelManager.init_model()
    ModelManager.update_model()

    class Application(tornado.web.Application):
        def __init__(self):
            handlers = [
                (r"/", MainHandler),
                (r"/show", ShowHandler),
                (r"/play", PlayHandler)
            ]

            settings = {
                'debug': True,
                'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
                'static_path': os.path.join(os.path.dirname(__file__), 'static')
            }
            tornado.web.Application.__init__(self, handlers, **settings)

    application = Application()

    application.listen(8888)
    print("Staring tornado loop ...")
    tornado.ioloop.IOLoop.instance().start()