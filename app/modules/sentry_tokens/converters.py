from werkzeug.routing import BaseConverter

from app.extensions.api import abort
from app.modules.sentry_tokens.models import SentryToken


class SentryTokenConverter(BaseConverter):
    def to_python(self, value):
        sentry_token = SentryToken.query.filter(SentryToken.id == value).first()
        if sentry_token:
            return sentry_token
        else:
            abort(404)
