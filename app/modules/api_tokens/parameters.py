from flask_login import current_user
from flask_marshmallow import base_fields

from .models import ApiToken
from flask_restplus_patched import PostFormParameters, PatchJSONParameters
from marshmallow import validates, ValidationError

from app.extensions.api.parameters import PaginationParameters

class ListApiTokensParameters(PaginationParameters):

    owner_id = base_fields.Integer()

    @validates('owner_id')
    def validateOwnerId(self, data):
        if hasattr(current_user, 'id'):
            if current_user.id != data and not (current_user.is_admin or current_user.is_internal):
                raise ValidationError("You can only query your own API tokens.")

class CreateApiTokenParameters(PostFormParameters):
    name = base_fields.String(required=True, description='Name of the API token')
    owner_id = base_fields.Integer(description='Owner of the token. Requires Admin to create for other users.')

    @validates('name')
    def validateName(self, data):
        if len(data) < 3:
            raise ValidationError(f"Name must be greater than 3 characters long.")

    @validates('owner_id')
    def validateUserId(self, data):
        if hasattr(current_user, 'id'):
            if current_user.id != data and not (current_user.is_admin or current_user.is_internal):
                raise ValidationError("You can only create API tokens for yourself.")


class PatchApiTokenDetailsParameters(PatchJSONParameters):
    """
    API Token details updating parameters following PATCH JSON RFC.
    """
    fields = (ApiToken.name.key, ApiToken.enabled.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)
