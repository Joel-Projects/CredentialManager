from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema, Schema

from ..bots.schemas import DetailedBotSchema
from ..database_credentials.schemas import DetailedDatabaseCredentialSchema
from ..reddit_apps.schemas import DetailedRedditAppSchema
from ..sentry_tokens.schemas import DetailedSentryTokenSchema
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

    _resource_type = Meta.model.__name__
    resource_type = base_fields.String(default=_resource_type)


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

    bots = base_fields.Nested(DetailedBotSchema, many=True)
    reddit_apps = base_fields.Nested(DetailedRedditAppSchema, many=True)
    sentry_tokens = base_fields.Nested(DetailedSentryTokenSchema, many=True)
    database_credentials = base_fields.Nested(DetailedDatabaseCredentialSchema, many=True)

    class Meta(BaseUserSchema.Meta):
        fields = BaseUserSchema.Meta.fields + (
            User.bots.key,
            User.reddit_apps.key,
            User.sentry_tokens.key,
            User.database_credentials.key,
        )
