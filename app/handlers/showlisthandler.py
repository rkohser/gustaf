import tornado
import json
from core.helpers import ModelEncoder
from model.modelqueries import query_shows_list_with_state


class ShowListHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def get(self):
        self.write(json.dumps(query_shows_list_with_state(), indent=4, cls=ModelEncoder))
