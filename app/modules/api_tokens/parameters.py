from flask_marshmallow import base_fields
from marshmallow import ValidationError, validates

from app.extensions.api.parameters import PaginationParameters, ValidateOwner
from flask_restplus_patched import PatchJSONParameters, PostFormParameters

from . import schemas
from .models import ApiToken


class ListApiTokensParameters(PaginationParameters, ValidateOwner):
    owner_id = base_fields.Integer()

    class Meta:
        model = ApiToken

    invalidOwnerMessage = "You can only query your own {}."


# #class CreateApiTokenParameters(PostFormParameters, schemas.BaseApiTokenSchema, ValidateOwner):
# #    name = base_fields.String(required=True, description='Name of the API token')
# #    owner_id = base_fields.Integer(description='Owner of the token. Requires Admin to create for other users.')
# #    length = base_fields.Integer(description='Length of the token. Must be between 16 and 128, `16<=length<=128`. Defaults to `32`', default=32)
# #
# #    class Meta(schemas.BaseApiTokenSchema.Meta):
# #        fields = schemas.BaseApiTokenSchema.Meta.fields + ('owner_id', 'length')
# #
# #    @validates('name')
# #    def validateName(self, data):
# #        if len(data) < 3:
# #            raise ValidationError('Name must be greater than 3 characters long.')
# #
# #    @validates('length')
# #    def validateLength(self, data):
# #        if 16 > data:
# #            raise ValidationError('Length must be greater than 16.')
# #        elif 128 < data:
# #            raise ValidationError('Length must be less than 128.')


class PatchApiTokenDetailsParameters(PatchJSONParameters):
    fields = (ApiToken.name.key, ApiToken.enabled.key)
    PATH_CHOICES = tuple(f"/{field}" for field in fields)
