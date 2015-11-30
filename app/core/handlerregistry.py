import tornado

_handlers = dict()


def register_handler(name, handler):
    assert isinstance(handler, tornado.web.RequestHandler)
    _handlers[name] = handler


def get_handler(name):
    return _handlers[name]
