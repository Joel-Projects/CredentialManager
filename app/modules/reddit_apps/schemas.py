from flask_marshmallow import base_fields
from flask_restplus_patched import ModelSchema

from .models import SentryToken


class BaseSentryTokenSchema(ModelSchema):
    """
    Base Sentry Token schema exposes only the most general fields.
    """
    class Meta:
        model = SentryToken
        fields = (
            SentryToken.id.key,
            SentryToken.name.key,
            SentryToken.dsn.key
        )


class DetailedSentryTokenSchema(BaseSentryTokenSchema):
    """
    Detailed Sentry Token schema exposes all useful fields.
    """

    class Meta(BaseSentryTokenSchema.Meta):
        fields = BaseSentryTokenSchema.Meta.fields + (
            SentryToken.owner_id.key,
            SentryToken.created.key,
        )
