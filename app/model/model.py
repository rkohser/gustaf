__author__ = 'roland'

from peewee import *


db = SqliteDatabase('gustaf.db')


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
    watched = BooleanField(default=False)


class Source(BaseModel):
    dir = CharField()