"""
Refresh Tokens module
==================
"""
import logging, praw
from app.extensions.api import api_v1

log = logging.getLogger(__name__)
reddit = praw.Reddit('credMgr')

def init_app(app, **kwargs):

    from . import models, views, converters, resources
    api_v1.add_namespace(resources.api)
    app.url_map.converters['RefreshToken'] = converters.RefreshTokenConverter
    app.register_blueprint(views.refreshTokensBlueprint)
