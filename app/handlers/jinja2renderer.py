__author__ = 'roland'

from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class Jinja2Renderer:
    def __init__(self, settings):
        self.settings = settings

    def render_template(self, template_name, **kwargs):
        template_dirs = []
        if self.settings.get('template_path', ''):
            template_dirs.append(
                self.settings["template_path"]
            )

        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content

    def render_string(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        kwargs.update({
            'settings': self.settings,
            'static_url': self.settings.get('static_url_prefix', '/static/'),
        })
        return self.render_template(template_name, **kwargs)