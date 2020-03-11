from flask_marshmallow import base_fields
from marshmallow import ValidationError, validates

from app.extensions.api.parameters import PaginationParameters, validateOwner
from flask_restplus_patched import PatchJSONParameters, PostFormParameters
from . import schemas
from .models import ApiToken


class ListApiTokensParameters(PaginationParameters, validateOwner):
    owner_id = base_fields.Integer()

    class Meta:
        model = ApiToken

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateApiTokenParameters(PostFormParameters, schemas.BaseApiTokenSchema, validateOwner):
    name = base_fields.String(required=True, description='Name of the API token')
    owner_id = base_fields.Integer(description='Owner of the token. Requires Admin to create for other users.')

    class Meta(schemas.BaseApiTokenSchema.Meta):
        fields = schemas.BaseApiTokenSchema.Meta.fields + ('owner_id',)

    @validates('name')
    def validateName(self, data):
        if len(data) < 3:
            raise ValidationError('Name must be greater than 3 characters long.')

class PatchApiTokenDetailsParameters(PatchJSONParameters):
    fields = (ApiToken.name.key, ApiToken.enabled.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)