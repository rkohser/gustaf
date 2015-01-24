__author__ = 'roland'

from peewee import *
from enum import Enum, unique

db = SqliteDatabase('gustaf.db')


@unique
class PlayState(Enum):
    NOT_WATCHED = (1, "Not watched", "label-danger")
    WATCHING = (2, "Watching", "label-waring")
    WATCHED = (3, "Watched", "label-success")

    def __init__(self, num, text, label):
        self.num = num
        self.text = text
        self.label = label

    @classmethod
    def from_num(cls, num):
        dic = {member.num: member for name, member in cls.__members__.items()}
        return dic[num]


class PlayStateField(IntegerField):
    def db_value(self, value):
        assert isinstance(value, PlayState)
        return str(value.num)

    def python_value(self, value):
        return PlayState.from_num(int(value))


class BaseModel(Model):
    class Meta:
        database = db


class Show(BaseModel):
    name = CharField()


class Season(BaseModel):
    show = ForeignKeyField(Show, related_name='seasons')
    number = IntegerField()


class Episode(BaseModel):
    season = ForeignKeyField(Season, related_name='episodes')
    number = IntegerField()
    path = CharField()
    current_time = FloatField(default=0.0)
    state = PlayStateField(default=PlayState.NOT_WATCHED)


class Source(BaseModel):
    dir = CharField()