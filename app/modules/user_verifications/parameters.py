from flask_marshmallow import base_fields

from app.extensions.api.parameters import PaginationParameters, validateOwner
from flask_restplus_patched import PatchJSONParameters, PostFormParameters
from . import schemas
from .models import UserVerification


class ListUserVerificationsParameters(PaginationParameters, validateOwner):
    owner_id = base_fields.Integer()
    redditor = base_fields.String()

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateUserVerificationParameters(PostFormParameters, schemas.BaseUserVerificationSchema, validateOwner):
    reddit_app_id = base_fields.Integer(required=True, description='Reddit app the User Verification is for')
    discord_id = base_fields.String(required=True, description='Discord member ID to associate Redditor with')
    redditor = base_fields.String(description='Redditor the User Verification is for')
    extra_data = base_fields.String(description='Extra data to include with verification', default='{}')

    class Meta(schemas.BaseUserVerificationSchema.Meta):
        fields = schemas.BaseUserVerificationSchema.Meta.fields

class GetUserVerificationByDiscordId(PostFormParameters):
    discord_id = base_fields.String(required=True, description='Discord member ID to associate Redditor with')
    reddit_app_id = base_fields.Integer(description='Optionally specify a Reddit app the User Verification belongs to')

class PatchUserVerificationDetailsParameters(PatchJSONParameters):
    '''
    User Verification details updating parameters following PATCH JSON RFC.
    '''
    fields = (UserVerification.reddit_app_id.key, UserVerification.discord_id.key, UserVerification.redditor.key, UserVerification.extra_data.key, UserVerification.enabled.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)