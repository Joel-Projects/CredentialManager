from flask_marshmallow import base_fields
from flask_restplus_patched import ModelSchema

from .models import Bot
from ..database_credentials.schemas import BaseDatabaseCredentialSchema
from ..reddit_apps.schemas import BaseRedditAppSchema
from ..sentry_tokens.schemas import BaseSentryTokenSchema


class BaseBotSchema(ModelSchema):
    """
    Base Bot schema exposes only the most general fields.
    """
    class Meta:
        model = Bot
        fields = (
            Bot.id.key,
            Bot.app_name.key,
            Bot.enabled.key
        )


class DetailedBotSchema(BaseBotSchema):
    """
    Detailed Bot schema exposes all useful fields.
    """
    reddit_app = base_fields.Nested(BaseRedditAppSchema)
    sentry_token = base_fields.Nested(BaseSentryTokenSchema)
    database_credentials = base_fields.Nested(BaseDatabaseCredentialSchema)

    class Meta(BaseBotSchema.Meta):
        fields = BaseBotSchema.Meta.fields + (
            Bot.owner_id.key,
            Bot.created.key,
            Bot.reddit_app.key,
            Bot.sentry_token.key,
            Bot.database_credential.key
        )
