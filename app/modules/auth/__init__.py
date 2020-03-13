import base64, logging

from flask_login import user_logged_in, login_user

from app.extensions import login_manager
from app.modules.users.models import User


log = logging.getLogger(__name__)

def loadUserFromRequest(request):
    user = None
    try:
        apiKey = request.headers.get('X-API-KEY', None)
        # auth = request.headers.get('authorization', None)
        if apiKey:
            user = User.findWithApiKey(apiKey)
        if not user:
            username = request.authorization['username']
            password = request.authorization['password']
            # username, password = base64.b64decode(auth.replace('Basic ', '', 1)).decode().split(':')
            if username and password:
                user = User.findWithPassword(username, password)
                if user and not user.is_active:
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