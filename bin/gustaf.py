__author__ = 'roland'

import sys
from gustaf_core.filefinder import FileFinder
from gustaf_core.filesorter import FileSorter, ConvenientShow, ConvenientSeason, ConvenientEpisode
from model.model import Show, Season, Episode


if __name__ == '__main__':

    if len(sys.argv) == 2:
        finder = FileFinder(sys.argv[1:])
        sorter = FileSorter()
        sorter.sort(finder.find())

        found_shows = sorter.shows

        for found_show in found_shows:
            show = Show(name=found_show.name)
            show.save()

            for found_season in found_show.seasons:
                season = Season(show=show, number=int(found_season.number))
                season.save()

                for found_episode in found_season.episodes:
                    episode = Episode(season=season, number=int(found_episode.number), path=found_episode.path)
                    episode.save()