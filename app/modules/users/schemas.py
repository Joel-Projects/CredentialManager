from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema
from .models import User
from ..database_credentials.schemas import BaseDatabaseCredentialSchema
from ..reddit_apps.schemas import BaseRedditAppSchema
from ..sentry_tokens.schemas import BaseSentryTokenSchema


class BaseUserSchema(ModelSchema):
    '''
    Base user schema exposes only the most general fields.
    '''

    class Meta:
        model = User
        fields = (
            User.id.key,
            User.username.key,
        )
        dump_only = (
            User.id.key,
        )

class DetailedUserSchema(BaseUserSchema):
    '''
    Detailed user schema exposes all useful fields.
    '''

    class Meta(BaseUserSchema.Meta):
        fields = (
            User.id.key,
            User.username.key,
            User.is_active.fget.__name__,
            User.is_regular_user.fget.__name__,
            User.is_admin.fget.__name__,
            User.default_settings.key,
            User.created.key,
            User.updated.key,
        )

class UserItemsSchema(BaseUserSchema):
    '''
    User items schema exposes all items.
    '''
    reddit_apps = base_fields.Nested(BaseRedditAppSchema, many=True)
    sentry_tokens = base_fields.Nested(BaseSentryTokenSchema, many=True)
    database_credentials = base_fields.Nested(BaseDatabaseCredentialSchema, many=True)

    class Meta(BaseUserSchema.Meta):
        fields = BaseUserSchema.Meta.fields + (
            User.reddit_apps.key,
            User.sentry_tokens.key,
            User.database_credentials.key,
            User.created.key,
            User.updated.key
        )