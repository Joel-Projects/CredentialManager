import logging

from app.extensions import login_manager
from app.modules.users.models import User

log = logging.getLogger(__name__)


def load_user_from_request(request):
    user = None
    log.info("load_user_from_request begin")
    try:
        api_token = request.headers.get("X-API-TOKEN", None)
        log.info("load_user_from_request got header")
        if api_token:
            user = User.find_with_api_token(api_token)
            log.info("load_user_from_request got user from api token")
        if not user:
            log.info("load_user_from_request getting username and password")
            username = getattr(request.authorization, "username", None)
            password = getattr(request.authorization, "password", None)
            if username and password:
                log.info("load_user_from_request got username and password")
                user = User.find_with_password(username, password)
                if user and not user.is_active:
                    user = None
    except Exception as error:
        log.exception(error)
    log.info("load_user_from_request returning user")
    return user


def init_app(app, **kwargs):
    login_manager.request_loader(load_user_from_request)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        log.info("load_user loading user")
        return User.query.get(int(user_id))

    from . import views

    app.register_blueprint(views.auth_blueprint)
