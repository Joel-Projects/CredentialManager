from flask_marshmallow import base_fields
from flask_restplus_patched import Schema, ModelSchema

from .models import User


class BaseUserSchema(ModelSchema):
    """
    Base user schema exposes only the most general fields.
    """

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
            User.default_redirect_uri.key,
            User.created.key,
            User.updated.key,
        )

class UserItemsSchema(BaseUserSchema):
    """
    Detailed user schema exposes all useful fields.
    """

    class Meta(BaseUserSchema.Meta):
        fields = BaseUserSchema.Meta.fields + (
            User.created.key,
            User.updated.key,
            User.is_active.fget.__name__,
            User.is_regular_user.fget.__name__,
            User.is_admin.fget.__name__,
        )
