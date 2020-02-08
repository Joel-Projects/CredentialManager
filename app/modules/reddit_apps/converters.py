from app.extensions.api import abort
from .models import RedditApp
from werkzeug.routing import BaseConverter

class RedditAppConverter(BaseConverter):

    def to_python(self, value):
        redditApp = RedditApp.query.filter(RedditApp.id == value).first()
        if redditApp:
            return redditApp
        else:
            abort(404)