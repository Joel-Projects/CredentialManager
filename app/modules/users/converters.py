from app.extensions.api import abort
from app.modules.users.models import User
from werkzeug.routing import BaseConverter

class UserConverter(BaseConverter):

    def to_python(self, value):
        return User.query.filter(User.username.ilike(value)).first_or_404()
