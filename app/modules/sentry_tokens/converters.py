from werkzeug.routing import BaseConverter

from app.extensions.api import abort
from app.modules.sentry_tokens.models import SentryToken


class SentryTokenConverter(BaseConverter):
    def to_python(self, value):
        sentryToken = SentryToken.query.filter(SentryToken.id == value).first()
        if sentryToken:
            return sentryToken
        else:
            abort(404)
