__author__ = 'roland'

import subliminal
import io

from babelfish import Language
from subliminal.subtitle import get_subtitle_path


def save_subtitle(video, video_subtitle, encoding=None):
    subtitle_path = get_subtitle_path(video.name, video_subtitle.language)
    if encoding is None:
        with io.open(subtitle_path, 'wb') as f:
            f.write(video_subtitle.content)
    else:
        with io.open(subtitle_path, 'w', encoding=encoding) as f:
            f.write(video_subtitle.text)
    return subtitle_path


def get_subs(episode_path):
    lang = {Language('eng'), Language('fra')}

    video = subliminal.scan_video(episode_path)
    if video:
        if lang.issubset(video.subtitle_languages):
            # already have subs
            print('Detected subtitles for "' + episode_path)
            return True
        else:
            subtitles = subliminal.download_best_subtitles({video, }, lang, providers=['opensubtitles', ])
            for vid, video_subtitles in subtitles.items():
                for sub in video_subtitles:
                    save_subtitle(vid, sub)
                if video_subtitles:
                    print('Downloaded subtitles for "' + episode_path)
                    return True

    return False

