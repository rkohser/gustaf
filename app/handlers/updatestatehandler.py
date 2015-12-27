import tornado
import json
from model.modelqueries import update_episode_status


class UpdateStateHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def put(self):
        data = json.loads(bytes.decode(self.request.body))

        update_episode_status(data)
