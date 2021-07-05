from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema, Schema

from ..database_credentials.schemas import BaseDatabaseCredentialSchema
from ..reddit_apps.schemas import BaseRedditAppSchema
from ..sentry_tokens.schemas import BaseSentryTokenSchema
from .models import User


class BaseUserSchema(ModelSchema):
    """
    Base user schema exposes only the most general fields.
    """

    class Meta:
        ordered = True
        model = User
        fields = (User.id.key, User.username.key, "resource_type")
        dump_only = (User.id.key, "resource_type")

    _resourceType = Meta.model.__name__
    resource_type = base_fields.String(default=_resourceType)


class DefaultSettings(Schema):
    database_flavor = base_fields.Str()
    database_host = base_fields.Str()
    ssh_host = base_fields.Str()
    ssh_user = base_fields.Str()
    user_agent = base_fields.Str()


class DetailedUserSchema(BaseUserSchema):
    """
    Detailed user schema exposes all useful fields.
    """

    class Meta(BaseUserSchema.Meta):
        fields = (
            User.id.key,
            User.username.key,
            User.is_active.fget.__name__,
            User.is_regular_user.fget.__name__,
            User.is_admin.fget.__name__,
            User.default_settings.key,
            User.reddit_username.key,
            User.created.key,
            User.updated.key,
            "resource_type",
        )


class UserItemsSchema(BaseUserSchema):
    """
    User items schema exposes all items.
    """

    reddit_apps = base_fields.Nested(BaseRedditAppSchema, many=True)
    sentry_tokens = base_fields.Nested(BaseSentryTokenSchema, many=True)
    database_credentials = base_fields.Nested(BaseDatabaseCredentialSchema, many=True)

    class Meta(BaseUserSchema.Meta):
        fields = BaseUserSchema.Meta.fields + (
            User.reddit_apps.key,
            User.sentry_tokens.key,
            User.database_credentials.key,
        )
