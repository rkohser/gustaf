import tornado
import json
from core.helpers import ModelEncoder
from model.modelqueries import query_episodes_per_show_id, query_started_episodes, query_added_episodes, query_next_episodes


class EpisodeHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def get(self, show_id=None):
        self.write(json.dumps(query_episodes_per_show_id(show_id), indent=4, cls=ModelEncoder))


class AddedEpisodesHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def get(self):
        self.write(json.dumps(query_added_episodes(), indent=4, cls=ModelEncoder))


class StartedEpisodesHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def get(self):
        self.write(json.dumps(query_started_episodes(), indent=4, cls=ModelEncoder))


class NextEpisodesHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def get(self):
        self.write(json.dumps(query_next_episodes(), indent=4, cls=ModelEncoder))
