# encoding: utf-8
"""
Auth module
===========
"""
import logging, base64
from datetime import timedelta

from app.extensions import login_manager
from flask_login import login_user, current_user
from app.modules.users.models import User

log = logging.getLogger(__name__)

def loadUserFromRequest(request):
    user = None
    try:
        auth = request.headers.get('authorization', None)
        apiKey = request.headers.get('X-API-KEY', None)
        if apiKey:
            user = User.findWithApiKey(apiKey)
        if auth and not user:
            username, password = base64.b64decode(auth.replace('Basic ', '', 1)).decode().split(':')
            if username and password:
                user = User.findWithPassword(username, password)
                if user and not user.is_enabled:
                    user = None
    except Exception as error:
        log.exception(error)
    return user

def init_app(app, **kwargs):

    login_manager.request_loader(loadUserFromRequest)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from . import views

    app.register_blueprint(views.auth_blueprint)
