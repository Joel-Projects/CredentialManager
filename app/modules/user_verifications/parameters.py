from flask_login import current_user
from flask_marshmallow import base_fields

from .models import UserVerification
from . import schemas
from flask_restplus_patched import PostFormParameters, PatchJSONParameters
from marshmallow import validates, ValidationError

from app.extensions.api.parameters import PaginationParameters, validateOwner

class ListUserVerificationsParameters(PaginationParameters, validateOwner):

    owner_id = base_fields.Integer()
    redditor = base_fields.String()

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateUserVerificationParameters(PostFormParameters, schemas.BaseUserVerificationSchema, validateOwner):
    reddit_app_id = base_fields.Integer(required=True, description='Reddit app the User Verification is for')
    discord_id = base_fields.String(required=True, description='Discord member ID to associate Redditor with')
    redditor = base_fields.String(description='Redditor the User Verification is for')
    extra_data = base_fields.Dict(description='Extra data to include with verification', default={})

    class Meta(schemas.BaseUserVerificationSchema.Meta):
        fields = schemas.BaseUserVerificationSchema.Meta.fields

class PatchUserVerificationDetailsParameters(PatchJSONParameters):
    """
    User Verification details updating parameters following PATCH JSON RFC.
    """
    fields = (UserVerification.reddit_app_id.key, UserVerification.discord_id.key, UserVerification.redditor.key, UserVerification.extra_data.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)
