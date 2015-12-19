import tornado
import json
from core.helpers import ModelEncoder
from model.modelqueries import query_episodes_per_show_id


class EpisodeHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def get(self, show_id=None):
        self.write(json.dumps(query_episodes_per_show_id(show_id), indent=4, cls=ModelEncoder))
