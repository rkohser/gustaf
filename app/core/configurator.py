import json

__settings__ = None


def init(path):
    global __settings__
    with open(path) as f:
        __settings__ = json.load(f)
        pass


def get():
    return __settings__
