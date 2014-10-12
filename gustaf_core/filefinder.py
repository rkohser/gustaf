__author__ = 'roland'

import sys

import os
import re


class FileFinder:
    reobj = re.compile(
        r'(?P<show_name>.*)\.[sS](?P<season_num>[0-9]+)[eE](?P<episode_num>[0-9]+)(?P<team>.*)\.(?P<extension>mkv|mp4|avi)')

    def __init__(self, dirs_):
        self._dirs = dirs_

    def find(self):
        files = list()

        #all dirs
        for _dir in self._dirs:

            #all files
            for file in os.listdir(_dir):
                m = self.reobj.match(file)
                if m:
                    file_dict = m.groupdict()
                    file_dict['path'] = file
                    files.append(file_dict)
        return files


if __name__ == '__main__':

    if len(sys.argv) == 2:
        finder = FileFinder(sys.argv[1:])
        duc = finder.find()
        print([x['show'] for x in duc])

