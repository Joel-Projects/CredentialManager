from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema

from ..database_credentials.schemas import DetailedDatabaseCredentialSchema
from ..reddit_apps.schemas import DetailedRedditAppSchema
from ..sentry_tokens.schemas import DetailedSentryTokenSchema
from .models import Bot


class BaseBotSchema(ModelSchema):
    """
    Base Bot schema exposes only the most general fields.
    """

    owner_id = base_fields.Integer(description="Owner of the bot. Requires Admin to create for other users.")

    class Meta:
        ordered = True
        model = Bot
        fields = (Bot.id.key, Bot.app_name.key, Bot.enabled.key, "resource_type")
        dump_only = (Bot.id.key, "resource_type")
        load_only = (Bot.enabled.key,)

    _resource_type = Meta.model.__name__
    resource_type = base_fields.String(default=_resource_type)


class DetailedBotSchema(BaseBotSchema):
    """
    Detailed Bot schema exposes all useful fields.
    """

    reddit_app = base_fields.Nested(DetailedRedditAppSchema, exclude=("enabled",))
    sentry_token = base_fields.Nested(DetailedSentryTokenSchema, exclude=("enabled",))
    database_credential = base_fields.Nested(DetailedDatabaseCredentialSchema, exclude=("enabled",))

    class Meta(BaseBotSchema.Meta):
        fields = BaseBotSchema.Meta.fields + (
            Bot.owner_id.key,
            Bot.reddit_app.key,
            Bot.sentry_token.key,
            Bot.database_credential.key,
        )
