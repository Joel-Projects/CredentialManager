from flask_marshmallow import base_fields
from flask_restplus_patched import ModelSchema

from .models import ApiToken


# noinspection PyTypeChecker
from ..users.schemas import BaseUserSchema


class BaseApiTokenSchema(ModelSchema):
    """
    Base API Token schema exposes only the most general fields.
    """
    name = base_fields.String(required=True)
    owner_id = base_fields.Integer()
    class Meta:
        model = ApiToken
        fields = (
            ApiToken.name.key,
            ApiToken.owner_id.key
        )
        dump_only = (
            ApiToken.name.key,
            ApiToken.owner_id.key,
        )


class DetailedApiTokenSchema(BaseApiTokenSchema):
    """
    Detailed API Token schema exposes all useful fields.
    """

    class Meta(BaseApiTokenSchema.Meta):
        fields = BaseApiTokenSchema.Meta.fields + (
            ApiToken.token.key,
        )
