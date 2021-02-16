from werkzeug.routing import BaseConverter

from app.extensions.api import abort
from .models import UserVerification


class UserVerificationConverter(BaseConverter):
    def to_python(self, value):
        userVerification = UserVerification.query.filter(
            UserVerification.id == value
        ).first()
        if userVerification:
            return userVerification
        else:
            abort(404)
