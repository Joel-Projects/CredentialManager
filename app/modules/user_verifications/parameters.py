import json

from flask_login import current_user
from flask_marshmallow import base_fields
from marshmallow import ValidationError, validates

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

    class Meta:
        model = UserVerification

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateUserVerificationParameters(PostFormParameters, schemas.DetailedUserVerificationSchema, ValidateOwner):
    reddit_app_id = base_fields.Integer(required=True, description='Reddit app the User Verification is for')
    user_id = base_fields.String(required=True, description='User ID to associate Redditor with')
    redditor = base_fields.String(description='Redditor the User Verification is for')
    extra_data = JSON(description='Extra JSON data to include with verification', default={})
    owner_id = base_fields.Integer(description='Owner of the verification. Requires Admin to create for other users.')

    @validates('reddit_app_id')
    def validateRedditApp(self, data):
        from app.modules.reddit_apps.models import RedditApp
        reddit_app = RedditApp.query.get(data)
        if not current_user.is_admin and not current_user.is_internal and not reddit_app.owner == current_user:
            raise ValidationError("You don't have the permission to create User Verifications with other users' Reddit Apps.")

class GetUserVerificationByUserId(PostFormParameters):
    user_id = base_fields.String(required=True, description='User ID to associate Redditor with')
    reddit_app_id = base_fields.Integer(description='Optionally specify a Reddit app the User Verification belongs to')

class GetUserVerificationByOTC(PostFormParameters):
    otc = base_fields.String(required=True, description='OTC Code to finish auth')

class PatchUserVerificationDetailsParameters(PatchJSONParameters):
    '''
    User Verification details updating parameters following PATCH JSON RFC.
    '''
    fields = (UserVerification.reddit_app_id.key, UserVerification.user_id.key, UserVerification.redditor.key, UserVerification.extra_data.key, UserVerification.enabled.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)