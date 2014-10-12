__author__ = 'roland'

# from gustaf_core.filefinder import FileFinder
# from gustaf_core.filesorter import FileSorter
# from model.model import Show, Season, Episode

from model import ModelManager


if __name__ == '__main__':
    ModelManager.init_model()

    ModelManager.update_model()