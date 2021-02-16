from werkzeug.routing import BaseConverter

from app.extensions.api import abort
from .models import RedditApp


class RedditAppConverter(BaseConverter):
    def to_python(self, value):
        redditApp = RedditApp.query.filter(RedditApp.id == value).first()
        if redditApp:
            return redditApp
        else:
            abort(404)
