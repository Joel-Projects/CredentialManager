from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema

from .models import ApiToken


class BaseApiTokenSchema(ModelSchema):
    """
    Base API Token schema exposes only the most general fields.
    """

    class Meta:
        ordered = True
        model = ApiToken
        fields = (ApiToken.id.key, ApiToken.name.key, "resource_type")
        dump_only = (ApiToken.id.key, "resource_type")

    _resource_type = Meta.model.__name__
    resource_type = base_fields.String(default=_resource_type)


class DetailedApiTokenSchema(BaseApiTokenSchema):
    """
    Detailed API Token schema exposes all useful fields.
    """

    class Meta(BaseApiTokenSchema.Meta):
        fields = BaseApiTokenSchema.Meta.fields + (
            ApiToken.token.key,
            ApiToken.owner_id.key,
            ApiToken.enabled.key,
            ApiToken.created.key,
            ApiToken.updated.key,
            ApiToken.last_used.key,
        )
