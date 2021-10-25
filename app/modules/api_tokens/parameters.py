from flask_marshmallow import base_fields

from app.extensions.api.parameters import PaginationParameters, ValidateOwner
from flask_restplus_patched import PatchJSONParameters

from .models import ApiToken


class ListApiTokensParameters(PaginationParameters, ValidateOwner):
    owner_id = base_fields.Integer()

    class Meta:
        model = ApiToken

    invalid_owner_message = "You can only query your own {}."


class PatchApiTokenDetailsParameters(PatchJSONParameters):
    fields = (ApiToken.name.key, ApiToken.enabled.key)
    PATH_CHOICES = tuple(f"/{field}" for field in fields)
