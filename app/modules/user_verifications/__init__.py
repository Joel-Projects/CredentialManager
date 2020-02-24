"""
User Verifications module
==================
"""
import logging, praw
from app.extensions.api import api_v1

log = logging.getLogger(__name__)

def init_app(app, **kwargs):

    from . import models, views, converters, resources
    api_v1.add_namespace(resources.api)
    app.url_map.converters['UserVerification'] = converters.UserVerificationConverter
    app.register_blueprint(views.userVerificationsBlueprint)
