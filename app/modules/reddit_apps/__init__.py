import logging

from app.extensions.api import api_v1

log = logging.getLogger(__name__)


def init_app(app, **kwargs):
    from . import converters, models, resources, views

    api_v1.add_namespace(resources.api)
    app.url_map.converters["RedditApp"] = converters.RedditAppConverter
    app.register_blueprint(views.reddit_apps_blueprint)
