from werkzeug.routing import BaseConverter

from app.extensions.api import abort

from .models import UserVerification


class UserVerificationConverter(BaseConverter):
    def to_python(self, value):
        user_verification = UserVerification.query.filter(UserVerification.id == value).first()
        if user_verification:
            return user_verification
        else:
            abort(404)
