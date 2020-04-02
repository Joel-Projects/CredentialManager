from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema
from .models import Bot
from ..database_credentials.schemas import DatabaseCredentialBotSchema
from ..reddit_apps.schemas import RedditAppBotSchema
from ..sentry_tokens.schemas import SentryTokenBotSchema


class BaseBotSchema(ModelSchema):
    '''
    Base Bot schema exposes only the most general fields.
    '''
    owner_id = base_fields.Integer(description='Owner of the bot. Requires Admin to create for other users.')

    class Meta:
        ordered = True
        model = Bot
        fields = (
            Bot.id.key,
            Bot.app_name.key,
            Bot.enabled.key
        )
        dump_only = (
            Bot.id.key,
        )

class DetailedBotSchema(BaseBotSchema):
    '''
    Detailed Bot schema exposes all useful fields.
    '''
    reddit_app = base_fields.Nested(RedditAppBotSchema)
    sentry_token = base_fields.Nested(SentryTokenBotSchema)
    database_credential = base_fields.Nested(DatabaseCredentialBotSchema)

    class Meta(BaseBotSchema.Meta):
        fields = BaseBotSchema.Meta.fields + (
            Bot.owner_id.key,
            Bot.reddit_app.key,
            Bot.sentry_token.key,
            Bot.database_credential.key
        )