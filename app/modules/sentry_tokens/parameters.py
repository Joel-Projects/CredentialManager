from flask_marshmallow import base_fields
from marshmallow import ValidationError, validates

from app.extensions.api.parameters import PaginationParameters, ValidateOwner
from flask_restplus_patched import PatchJSONParameters, PostFormParameters

from . import schemas
from .models import SentryToken


class ListSentryTokensParameters(PaginationParameters, ValidateOwner):
    owner_id = base_fields.Integer()

    class Meta:
        model = SentryToken

    invalid_owner_message = "You can only query your own {}."


class CreateSentryTokenParameters(
    PostFormParameters, schemas.BaseSentryTokenSchema, ValidateOwner
):
    app_name = base_fields.String(required=True, description="Name of the Sentry Token")
    dsn = base_fields.String(required=True, description="DSN of the Sentry Token")
    owner_id = base_fields.Integer(
        description="Owner of the token. Requires Admin to create for other users."
    )

    class Meta(schemas.BaseSentryTokenSchema.Meta):
        fields = schemas.BaseSentryTokenSchema.Meta.fields + ("owner_id",)

    @validates("app_name")
    def validate_name(self, data):
        if len(data) < 3:
            raise ValidationError("Name must be greater than 3 characters long.")


class PatchSentryTokenDetailsParameters(PatchJSONParameters):
    """
    Sentry Token details updating parameters following PATCH JSON RFC.
    """

    fields = (SentryToken.app_name.key, SentryToken.dsn.key, SentryToken.enabled.key)
    PATH_CHOICES = tuple(f"/{field}" for field in fields)
