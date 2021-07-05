from werkzeug.routing import BaseConverter

from app.extensions.api import abort

from .models import RedditApp


class RedditAppConverter(BaseConverter):
    def to_python(self, value):
        reddit_app = RedditApp.query.filter(RedditApp.id == value).first()
        if reddit_app:
            return reddit_app
        else:
            abort(404)
