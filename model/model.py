__author__ = 'roland'

from peewee import *


db = SqliteDatabase('gustaf.db')


class Show(Model):
    name = CharField()

    class Meta:
        database = db


class Season(Model):
    show = ForeignKeyField(Show, related_name='season')
    number = IntegerField()

    class Meta:
        database = db


class Episode(Model):
    season = ForeignKeyField(Season, related_name='episode')
    number = IntegerField()
    path = CharField()

    class Meta:
        database = db


class Source(Model):
    dir = CharField()

    class Meta:
        database = db