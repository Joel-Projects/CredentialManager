import json

from flask_marshmallow import base_fields

from app.extensions.api.parameters import PaginationParameters, ValidateOwner
from flask_restplus_patched import PatchJSONParameters, PostFormParameters
from . import schemas
from .models import UserVerification


class JSON(base_fields.Field):

    default_error_messages = {
        'empty': 'Empty JSON payload.',
        'invalid': 'Unable to accept JSON payload.'
    }

    def _deserialize(self, value, attr, obj):
        try:
            data = json.loads(value)
            if not data:  # pragma: no cover
                self.fail('empty')
            return data
        except json.decoder.JSONDecodeError:  # pragma: no cover
            self.fail('invalid')

class ListUserVerificationsParameters(PaginationParameters, ValidateOwner):
    owner_id = base_fields.Integer()
    redditor = base_fields.String()

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateUserVerificationParameters(PostFormParameters, schemas.DetailedUserVerificationSchema, ValidateOwner):
    reddit_app_id = base_fields.Integer(required=True, description='Reddit app the User Verification is for')
    discord_id = base_fields.Integer(required=True, description='Discord member ID to associate Redditor with')
    redditor = base_fields.String(description='Redditor the User Verification is for')
    extra_data = JSON(description='Extra JSON data to include with verification', default={})
    owner_id = base_fields.Integer(description='Owner of the verification. Requires Admin to create for other users.')

class GetUserVerificationByDiscordId(PostFormParameters):
    discord_id = base_fields.String(required=True, description='Discord member ID to associate Redditor with')
    reddit_app_id = base_fields.Integer(description='Optionally specify a Reddit app the User Verification belongs to')

class PatchUserVerificationDetailsParameters(PatchJSONParameters):
    '''
    User Verification details updating parameters following PATCH JSON RFC.
    '''
    fields = (UserVerification.reddit_app_id.key, UserVerification.discord_id.key, UserVerification.redditor.key, UserVerification.extra_data.key, UserVerification.enabled.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)