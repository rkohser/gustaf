from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from core.customfilters import *


class Jinja2Renderer:
    def __init__(self, settings):
        self.settings = settings

        template_dirs = []
        if self.settings.get('template_path', ''):
            template_dirs.append(self.settings["template_path"])
        self.env = env = Environment(loader=FileSystemLoader(template_dirs))

        # custom filters
        self.env.filters['episode_progress'] = episode_progress
        self.env.filters['show_state'] = show_state
        self.env.filters['season_state'] = season_state
        self.env.filters['started_episodes'] = started_episodes
        self.env.filters['next_episodes'] = next_episodes

    def render_template(self, template_name, **kwargs):

        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content

    def render_string(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        :param kwargs:
        :param template_name:
        """
        kwargs.update({
            'settings': self.settings,
            'static_url': self.settings.get('static_url_prefix', '/static/'),
        })
        return self.render_template(template_name, **kwargs)
