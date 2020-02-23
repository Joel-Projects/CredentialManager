from app.extensions.api import abort
from .models import RefreshToken
from werkzeug.routing import BaseConverter

class RefreshTokenConverter(BaseConverter):

    def to_python(self, value):
        refreshToken = RefreshToken.query.filter(RefreshToken.id == value).first()
        if refreshToken:
            return refreshToken
        else:
            abort(404)