__author__ = 'roland'

import re
from peewee import DoesNotExist

from model import Show, Season, Episode, db
from modules import FileFinder


class ModelManager:
    episodes = None
    _name_sep = re.compile(r'\W+')

    @staticmethod
    def init_model():
        tables = [Show, Season, Episode]
        # db.drop_tables(tables)
        db.create_tables(tables, True)

    @staticmethod
    def clear_model():
        Episode.delete()
        Season.delete()
        Show.delete()

    @staticmethod
    def update_model():

        finder = FileFinder(['E:\JDownloader'])
        for episode in finder.find():
            ModelManager.merge_episode(episode)

    @staticmethod
    def merge_episode(episode):

        # Split the name
        show_name = ModelManager.normalize_name(episode['show_name'])
        parsed_season = episode['season_num']
        parsed_episode = episode['episode_num']

        try:
            show = Show.get(Show.name == show_name)
        except DoesNotExist:
            # Show does not exist yet
            show = Show.create(name=show_name)
            season = Season.create(show=show, number=parsed_season)
            Episode.create(season=season, number=parsed_episode, path=episode['path'])
        else:
            try:
                season = Season.get(Season.show == show, Season.number == parsed_season)
            except DoesNotExist:
                # Season did not exist yet
                season = Season.create(show=show, number=parsed_season)
                Episode.create(season=season, number=parsed_episode, path=episode['path'])
            else:
                try:
                    episode = Episode.get(Episode.season == season, Episode.number == parsed_episode)
                except DoesNotExist:
                    Episode.create(season=season, number=parsed_episode, path=episode['path'])
                    print('Merged "' + show.name + '" season ' + parsed_season + ' episode ' + parsed_episode)
                    # else:
                    #print('"' + show.name + '" season ' + parsed_season + ' episode ' + parsed_episode + ' already in db')

    @staticmethod
    def normalize_name(raw_name):
        """
        Normalizes a show name
        :param raw_name:
        :return:
        """
        return ' '.join(ModelManager._name_sep.split(raw_name.lower()))