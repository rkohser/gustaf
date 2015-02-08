__author__ = 'roland'

from model import PlayState
from enum import Enum, unique
import json


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)


@unique
class MessageType(Enum):
    LOAD_SHOW = "load_show"
    UPDATE_EPISODE_STATE = "update_episode_state"
    UPDATE_SEASON_STATE = "update_season_state"
    UPDATE_SHOW_STATE = "update_show_state"

    def __init__(self, text):
        self.text = text

    @classmethod
    def from_text(cls, text):
        dic = {member.text: member for name, member in cls.__members__.items()}
        return dic[text]


class Message(object):
    """
    Handles message from the websocket
    message:
    {
        "type": "load_show"|"update_episode_state"|"update_season_state"|"update_show_state"
        "episode_id": int id
        "season_id": int id
        "show_id": int id
        "state": json_dump from a model state enum
        "data": ex:html content
    }
    """

    def __init__(self, message_type, episode_id=None, season_id=None, show_id=None, state=None, data=None):
        assert isinstance(message_type, MessageType)
        self.message_type = message_type
        self.episode_id = episode_id
        self.season_id = season_id
        self.show_id = show_id
        self.state = state
        self.data = data

    def to_json(self):
        msg = dict()
        msg['action'] = self.message_type.text
        if self.message_type == MessageType.LOAD_SHOW:
            msg['show_id'] = self.show_id
            msg['data'] = self.data
        elif self.message_type == MessageType.UPDATE_EPISODE_STATE:
            msg['episode_id'] = self.episode_id
            msg['state'] = self.state.value
        elif self.message_type == MessageType.UPDATE_SEASON_STATE:
            msg['season_id'] = self.season_id
            msg['state'] = self.state.value
        return json.dumps(msg)

    @staticmethod
    def to_json(msg_list):
        # transform into dict list
        return json.dumps([msg.__dict__ for msg in msg_list], cls=EnumEncoder)


def parse_message(msg):
    d = json.loads(msg)
    mt = MessageType.from_text(d['action'])
    if mt == MessageType.LOAD_SHOW:
        return Message(mt, show_id=d['show_id'])
    elif mt == MessageType.UPDATE_EPISODE_STATE:
        return Message(mt, episode_id=d['episode_id'], state=PlayState.from_text(d['state']))
    elif mt == MessageType.UPDATE_SEASON_STATE:
        return Message(mt, season_id=d['season_id'], state=PlayState.from_text(d['state']))
    elif mt == MessageType.UPDATE_SHOW_STATE:
        return Message(mt, show_id=d['show_id'], state=PlayState.from_text(d['state']))

