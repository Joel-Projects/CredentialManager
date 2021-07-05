import base64
import logging

from flask_login import login_user, user_logged_in

from app.extensions import login_manager
from app.modules.users.models import User

log = logging.getLogger(__name__)


def loadUserFromRequest(request):
    user = None
    try:
        api_token = request.headers.get("X-API-TOKEN", None)
        if api_token:
            user = User.findWithApiToken(api_token)
        if not user:
            username = getattr(request.authorization, "username", None)
            password = getattr(request.authorization, "password", None)
            if username and password:
                user = User.findWithPassword(username, password)
                if user and not user.is_active:
                    user = None
    except Exception as error:
        log.exception(error)
    return user


def init_app(app, **kwargs):
    login_manager.request_loader(loadUserFromRequest)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from . import views

    app.register_blueprint(views.auth_blueprint)
