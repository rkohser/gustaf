__author__ = 'roland'

import re
from peewee import DoesNotExist

from model import Show, Season, Episode, db
from core import FileFinder
from core import get_subs


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

        db_ = list()
        for episode in Episode.select():
            db_.append(episode.path)
        finder = FileFinder(['E:\JDownloader'], db_, ("mkv", "avi", "mp4"))
        for episode_info in finder.find():
            ModelManager.merge_episode(episode_info)

    @staticmethod
    def merge_episode(episode_info):

        # Split the name
        path, info = episode_info
        show_name = info['series'].lower()
        parsed_season = info['season']
        parsed_episode = info['episodeNumber']

        languages = {'eng', 'fra'}

        try:
            show = Show.get(Show.name == show_name)
        except DoesNotExist:
            # Show does not exist yet
            show = Show.create(name=show_name)
            season = Season.create(show=show, season_number=parsed_season)
            Episode.create(season=season, episode_number=parsed_episode, path=path, subtitles=get_subs(path, languages))
            print('Merged "' + show.name + '" season ' + str(parsed_season) + ' episode ' + str(parsed_episode))
        else:
            try:
                season = Season.get(Season.show == show, Season.season_number == parsed_season)
            except DoesNotExist:
                # Season did not exist yet
                season = Season.create(show=show, season_numbernumber=parsed_season)
                Episode.create(season=season, episode_number=parsed_episode, path=path,
                               subtitles=get_subs(path, languages))
                print('Merged "' + show.name + '" season ' + str(parsed_season) + ' episode ' + str(parsed_episode))
            else:
                try:
                    Episode.get(Episode.season == season, Episode.episode_number == parsed_episode)
                except DoesNotExist:
                    Episode.create(season=season, episode_number=parsed_episode, path=path,
                                   subtitles=get_subs(path, languages))
                    print('Merged "' + show.name + '" season ' + str(parsed_season) + ' episode ' + str(parsed_episode))
                    # else:
                    #print('"' + show.name + '" season ' + parsed_season + ' episode ' + parsed_episode + ' already in db')