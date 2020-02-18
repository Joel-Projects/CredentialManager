from app.extensions.api import abort
from app.modules.bots.models import Bot
from werkzeug.routing import BaseConverter

class BotConverter(BaseConverter):

    def to_python(self, value):
        bot = Bot.query.filter(Bot.id == value).first()
        if bot:
            return bot
        else:
            abort(404)