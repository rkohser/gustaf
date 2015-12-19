from enum import Enum, unique
import json

from model import PlayState
from core.helpers import ModelEncoder


@unique
class MessageType(Enum):
    LOAD_SHOW = "load_show"
    UPDATE_EPISODE_STATE = "update_episode_state"
    UPDATE_SEASON_STATE = "update_season_state"
    UPDATE_SHOW_STATE = "update_show_state"
    PLAY_EPISODE = "play_episode"
    GET_SUBTITLES = "get_subtitles"

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
        "type": "load_show"|"update_episode_state"|"update_season_state"|"update_show_state"|"get_subtitles"
        "episode_id": int id
        "season_id": int id
        "show_id": int id
        "show_name": name of the show
        "state": json_dump from a model state enum
        "data": ex:html content
        "language": ex:"eng"
        "current_time": float
        "total_time": float
        "play_state": "playing"|"stopped"|"paused"
    }
    """

    def __init__(self, message_type, episode_id=None, season_id=None, show_id=None, show_name=None, state=None,
                 data=None, result=None,
                 lang=None, current_time=None, total_time=None, play_state=None):
        assert isinstance(message_type, MessageType)
        self.message_type = message_type
        self.episode_id = episode_id
        self.season_id = season_id
        self.show_id = show_id
        self.show_name = show_name
        self.state = state
        self.data = data
        self.result = result
        self.lang = lang
        self.current_time = current_time
        self.total_time = total_time
        self.play_state = play_state

    @staticmethod
    def to_json(msg_list):
        # transform into dict list
        return json.dumps([msg.__dict__ for msg in msg_list], cls=ModelEncoder)


def parse_message(msg):
    d = json.loads(msg)
    mt = MessageType.from_text(d['action'])
    if mt == MessageType.LOAD_SHOW:
        return Message(mt, show_id=d['show_id'], show_name=d['show_name'])
    elif mt == MessageType.UPDATE_EPISODE_STATE:
        return Message(mt, episode_id=d['episode_id'])
    elif mt == MessageType.UPDATE_SEASON_STATE:
        return Message(mt, season_id=d['season_id'], state=PlayState.from_text(d['state']))
    elif mt == MessageType.UPDATE_SHOW_STATE:
        return Message(mt, show_id=d['show_id'], state=PlayState.from_text(d['state']))
    elif mt == MessageType.PLAY_EPISODE:
        return Message(mt, episode_id=d['episode_id'])
    elif mt == MessageType.GET_SUBTITLES:
        return Message(mt, episode_id=d['episode_id'], lang=d['lang'])
