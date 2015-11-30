import os
import guessit


class FileFinder:
    def __init__(self, dirs_, db=list(), types=list()):
        self._dirs = dirs_
        self.db = db
        self.types = types

    def find(self):
        file_info = list()

        for dir_ in self._dirs:
            for root, dummy, files_ in os.walk(dir_):
                for filename in files_:
                    path = os.path.join(root, filename)
                    if filename.endswith(self.types) and path not in self.db:
                        info = guessit.guess_file_info(path)
                        if info and info["type"] == "episode":
                            file_info.append((path, info))
        return file_info

