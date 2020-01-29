from flask_login import current_user
from flask_marshmallow import base_fields

from .models import ApiToken
from . import schemas
from flask_restplus_patched import PostFormParameters, PatchJSONParameters
from marshmallow import validates, ValidationError

from app.extensions.api.parameters import PaginationParameters, validateOwner

class ListApiTokensParameters(PaginationParameters, validateOwner):

    owner_id = base_fields.Integer()

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateApiTokenParameters(PostFormParameters, schemas.BaseApiTokenSchema, validateOwner):
    name = base_fields.String(required=True, description='Name of the API token')
    owner_id = base_fields.Integer(description='Owner of the token. Requires Admin to create for other users.')

    class Meta(schemas.BaseApiTokenSchema.Meta):
        fields = schemas.BaseApiTokenSchema.Meta.fields + ('owner_id',)

    @validates('name')
    def validateName(self, data):
        if len(data) < 3:
            raise ValidationError("Name must be greater than 3 characters long.")

class PatchApiTokenDetailsParameters(PatchJSONParameters):
    """
    API Token details updating parameters following PATCH JSON RFC.
    """
    fields = (ApiToken.name.key, ApiToken.enabled.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)
