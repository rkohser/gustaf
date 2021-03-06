import re
import datetime
from peewee import DoesNotExist

from model import Show, Season, Episode, db, PlayState
from core import FileFinder
from core import get_subs
from core import configurator


class ModelManager:
    episodes = None
    _name_sep = re.compile(r'\W+')
    
    @staticmethod
    def refresh():
        ModelManager.init_model()
        ModelManager.update_model()
        ModelManager.update_subtitles()

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

        searchpath = configurator.get()['settings']['search_path']

        finder = FileFinder([searchpath], db_, ("mkv", "avi", "mp4"))
        for episode_info in finder.find():
            ModelManager.merge_episode(episode_info)

    @staticmethod
    def merge_episode(episode_info):

        # Split the name
        path, info = episode_info
        show_name = info['series'].lower()
        parsed_season = info['season']
        parsed_episode = info['episodeNumber']

        try:
            show = Show.get(Show.name == show_name)
        except DoesNotExist:
            # Show does not exist yet
            show = Show.create(name=show_name)
            season = Season.create(show=show, season_number=parsed_season)
            Episode.create(season=season, episode_number=parsed_episode, path=path, added_time=datetime.datetime.now())
            print('Merged "' + show.name + '" season ' + str(parsed_season) + ' episode ' + str(parsed_episode))
        else:
            try:
                season = Season.get(Season.show == show, Season.season_number == parsed_season)
            except DoesNotExist:
                # Season did not exist yet
                season = Season.create(show=show, season_number=parsed_season)
                Episode.create(season=season, episode_number=parsed_episode, path=path,
                               added_time=datetime.datetime.now())
                print('Merged "' + show.name + '" season ' + str(parsed_season) + ' episode ' + str(parsed_episode))
            else:
                try:
                    Episode.get(Episode.season == season, Episode.episode_number == parsed_episode)
                except DoesNotExist:
                    Episode.create(season=season, episode_number=parsed_episode, path=path,
                                   added_time=datetime.datetime.now())
                    print('Merged "' + show.name + '" season ' + str(parsed_season) + ' episode ' + str(parsed_episode))
                    # else:
                    # print('"' + show.name + '" season ' + parsed_season + ' episode ' + parsed_episode + ' already in db')

    @staticmethod
    def update_subtitles():

        languages = {'eng', 'fra'}

        for episode in Episode.select().where(Episode.episode_state == PlayState.NOT_WATCHED):

            existing_subs = episode.subtitles
            if not languages.issubset(existing_subs):
                new_subs = get_subs(episode.path, languages)
                if new_subs:
                    episode.subtitles = existing_subs.union(new_subs)
                    episode.save()
                    print('Found subtitles"' + str(new_subs) + ' for episode "' + episode.path + '"')



