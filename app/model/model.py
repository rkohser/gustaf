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
    number = CharField()


class Episode(BaseModel):
    season = ForeignKeyField(Season, related_name='episodes')
    number = CharField()
    path = CharField()


class Source(BaseModel):
    dir = CharField()