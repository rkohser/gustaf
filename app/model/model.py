__author__ = 'roland'

from enum import Enum, unique

from peewee import *


db = SqliteDatabase('gustaf.db')

# Print all queries to stderr.
import logging

logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@unique
class PlayState(Enum):
    NOT_WATCHED = (1, "Not watched", "danger")
    WATCHING = (2, "Watching", "warning")
    WATCHED = (3, "Watched", "success")

    def __init__(self, num, text, label):
        self.num = num
        self.text = text
        self.label = label

    @classmethod
    def from_num(cls, num):
        dic = {member.num: member for name, member in cls.__members__.items()}
        return dic[num]

    @classmethod
    def from_text(cls, text):
        dic = {member.text: member for name, member in cls.__members__.items()}
        return dic[text.strip()]

    def next(self):
        if self == PlayState.NOT_WATCHED or self == PlayState.WATCHING:
            return PlayState.WATCHED
        elif self == PlayState.WATCHED:
            return PlayState.NOT_WATCHED


class PlayStateField(IntegerField):
    def db_value(self, value):
        assert isinstance(value, PlayState)
        return str(value.num)

    def python_value(self, value):
        return PlayState.from_num(int(value))


class SubtitlesField(CharField):
    def db_value(self, value):
        assert isinstance(value, set)
        return ','.join(value)

    def python_value(self, value):
        if value:
            return set(value.split(','))
        else:
            return set()


class BaseModel(Model):
    class Meta:
        database = db


class Show(BaseModel):
    name = CharField()


class Season(BaseModel):
    show = ForeignKeyField(Show, related_name='seasons')
    season_number = IntegerField()


class Episode(BaseModel):
    season = ForeignKeyField(Season, related_name='episodes')
    episode_number = IntegerField()
    path = CharField()
    subtitles = SubtitlesField(default=set())
    current_time = FloatField(default=0.0)
    total_time = FloatField(default=0.0)
    episode_state = PlayStateField(default=PlayState.NOT_WATCHED)
    last_watched = DateTimeField()


class Source(BaseModel):
    dir = CharField()