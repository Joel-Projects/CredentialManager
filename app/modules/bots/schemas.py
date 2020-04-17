from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema
from .models import Bot
from ..database_credentials.schemas import DetailedDatabaseCredentialSchema
from ..reddit_apps.schemas import DetailedRedditAppSchema
from ..sentry_tokens.schemas import DetailedSentryTokenSchema


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
            Bot.enabled.key,
            'resource_type'
        )
        dump_only = (
            Bot.id.key,
            'resource_type'
        )

    _resourceType = Meta.model.__name__
    resource_type = base_fields.String(default=_resourceType)

class DetailedBotSchema(BaseBotSchema):
    '''
    Detailed Bot schema exposes all useful fields.
    '''
    reddit_app = base_fields.Nested(DetailedRedditAppSchema, exclude=('enabled', 'owner_id'))
    sentry_token = base_fields.Nested(DetailedSentryTokenSchema, exclude=('enabled', 'owner_id'))
    database_credential = base_fields.Nested(DetailedDatabaseCredentialSchema, exclude=('enabled', 'owner_id'))

    class Meta(BaseBotSchema.Meta):
        fields = BaseBotSchema.Meta.fields + (
            Bot.owner_id.key,
            Bot.reddit_app.key,
            Bot.sentry_token.key,
            Bot.database_credential.key
        )