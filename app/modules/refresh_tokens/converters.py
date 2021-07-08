from werkzeug.routing import BaseConverter

from app.extensions.api import abort

from .models import RefreshToken


class RefreshTokenConverter(BaseConverter):
    def to_python(self, value):
        refresh_token = RefreshToken.query.filter(RefreshToken.id == value).first()
        if refresh_token:
            return refresh_token
        else:
            abort(404)
