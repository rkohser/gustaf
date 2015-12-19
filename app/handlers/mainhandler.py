import tornado.web
from peewee import fn
from model import Show, Season, Episode, PlayState
from core import Jinja2Renderer


class MainHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.renderer = Jinja2Renderer(self.settings)

    def get(self):
        shows = (Show.select(Show, Season, Episode)
                 .join(Season)
                 .join(Episode)
                 .order_by(Show.name)
                 .aggregate_rows())

        # Build dashboard info
        started_episodes = (Episode.select(Show.name.alias('show_name'),
                                           Season.season_number.alias('season_number'),
                                           Episode)
                            .join(Season)
                            .join(Show)
                            .where(Episode.episode_state == PlayState.WATCHING)
                            .order_by(Episode.last_watched.desc())
                            .dicts())

        next_episodes = (Episode.select(Show.name.alias('show_name'),
                                        Season.season_number.alias('season_number'),
                                        fn.Min(Episode.episode_number).alias('episode_number'),
                                        Episode)
                         .join(Season)
                         .join(Show)
                         .where(Episode.episode_state == PlayState.NOT_WATCHED)
                         .group_by(Show.id)
                         .having(Episode.episode_number > 1)
                         .order_by(Episode.added_time.desc())
                         .dicts())

        self.write(self.renderer.render_string("shows.html", shows=shows, languages={'eng', 'fra'},
                                               next_episodes=next_episodes,
                                               PlayState=PlayState))
