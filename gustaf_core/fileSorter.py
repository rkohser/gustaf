__author__ = 'roland'

import re
import sys
from gustaf_core.filefinder import FileFinder


class FileSorter:
    # separator is any alphanumeric character

    def __init__(self):
        self._name_sep = re.compile(r'\W+')
        self.shows = list()

    def clear(self):
        self.shows.clear()

    def sort(self, files):

        #filename is a dictionnary
        for filename, filedict in files.items():
            #Split the name
            show_split = self._name_sep.split(filedict['show'].lower())
            parsed_season = filedict['season_num']
            parsed_episode = filedict['episode_num']

            show = self.seek_existing_show(show_split)
            if not show:
                show = ConvenientShow(name=' '.join(show_split))
                self.shows.append(show)

            season = FileSorter.seek_existing_season(show, parsed_season)
            if not season:
                season = ConvenientSeason(number=parsed_season)
                show.seasons.append(season)

            episode = FileSorter.seek_existing_episode(season, parsed_episode)
            if not episode:
                episode = ConvenientEpisode(parsed_episode, filename)
                season.episodes.append(episode)

    def seek_existing_show(self, from_file):

        for show in self.shows:
            from_list = self._name_sep.split(show.name.lower())
            if from_list == from_file:
                #same show
                return show

    def seek_existing_season(show, number):

        for season in show.seasons:
            if season.number == number:
                return season

    def seek_existing_episode(season, number):

        for episode in season.episodes:
            if episode.number == number:
                return episode


class ConvenientShow:
    def __init__(self, name):
        self.name = name
        self.seasons = list()


class ConvenientSeason:
    def __init__(self, number):
        self.number = number
        self.episodes = list()


class ConvenientEpisode:
    def __init__(self, number, path):
        self.number = number
        self.path = path

if __name__ == '__main__':

    if len(sys.argv) == 2:
        finder = FileFinder(sys.argv[1:])
        sorter = FileSorter()
        sorter.sort(finder.find())

        print([show.name for show in sorter.shows])
        print([season.number for season in sorter.shows.pop().seasons])