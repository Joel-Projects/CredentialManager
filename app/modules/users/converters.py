from werkzeug.routing import BaseConverter

from app.modules.users.models import User


class UserConverter(BaseConverter):

    def to_python(self, value):
        return User.query.filter(User.username.ilike(value)).first_or_404()