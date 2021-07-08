from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema, Schema

from .models import SentryToken


class BaseSentryTokenSchema(ModelSchema):
    """
    Base Sentry Token schema exposes only the most general fields.
    """

    class Meta:
        ordered = True
        model = SentryToken
        fields = (
            SentryToken.id.key,
            SentryToken.app_name.key,
            SentryToken.dsn.key,
            SentryToken.enabled.key,
            "resource_type",
        )
        dump_only = (SentryToken.id.key, "resource_type")
        load_only = (SentryToken.enabled.key,)

    _resource_type = Meta.model.__name__
    resource_type = base_fields.String(default=_resource_type)


class DetailedSentryTokenSchema(BaseSentryTokenSchema):
    """
    Detailed Sentry Token schema exposes all useful fields.
    """

    class Meta(BaseSentryTokenSchema.Meta):
        fields = BaseSentryTokenSchema.Meta.fields + (SentryToken.owner_id.key,)


class OrganizationSchema(Schema):
    id = base_fields.Str()
    name = base_fields.Str()
    slug = base_fields.Str()
