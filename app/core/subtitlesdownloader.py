import subliminal
import io

from babelfish import Language


def get_subtitle_path(video_path, video_language):
    video_extension = video_path.rsplit(".", 1)[-1]
    return video_path.replace(video_extension, video_language.alpha3 + ".srt")


def save_subtitle(video, video_subtitle, encoding=None):
    subtitle_path = get_subtitle_path(video.name, video_subtitle.language)
    if encoding is None:
        with io.open(subtitle_path, 'wb') as f:
            f.write(video_subtitle.content)
    else:
        with io.open(subtitle_path, 'w', encoding=encoding) as f:
            f.write(video_subtitle.text)
    return subtitle_path


def get_subs(episode_path, language_codes):
    lang = {Language(x) for x in language_codes}

    result = set()
    video = subliminal.scan_video(episode_path)
    if video:
        if lang.issubset(video.subtitle_languages):
            # already have subs
            print('Detected subtitles for "' + episode_path)
            for language in lang:
                result.add(language.alpha3)
        else:
            subtitles = subliminal.download_best_subtitles({video, }, lang,
                                                           providers=['opensubtitles', 'podnapisi'])
            for vid, video_subtitles in subtitles.items():
                if video_subtitles:
                    for sub in video_subtitles:
                        print('Downloaded subtitles "' + save_subtitle(vid, sub) + '" for "' + episode_path + '"')
                        result.add(sub.language.alpha3)

    return result
