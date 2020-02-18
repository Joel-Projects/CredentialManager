"""
Bots module
===========
"""
import logging
from app.extensions.api import api_v1

log = logging.getLogger(__name__)

def init_app(app, **kwargs):

    from . import models, views, resources, converters

    api_v1.add_namespace(resources.api)
    app.url_map.converters['Bot'] = converters.BotConverter
    app.register_blueprint(views.botsBlueprint)
