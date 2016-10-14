from model import ModelManager
import tornado

class RefreshHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def get(self):
		ModelManager.refresh()
        self.write("ok")