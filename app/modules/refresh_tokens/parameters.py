from flask_marshmallow import base_fields

from app.extensions.api.parameters import PaginationParameters, validateOwner
from flask_restplus_patched import Parameters, PatchJSONParameters, PostFormParameters
from . import schemas
from .models import RefreshToken


class ListRefreshTokensParameters(PaginationParameters, validateOwner):
    owner_id = base_fields.Integer()
    redditor = base_fields.String()

    invalidOwnerMessage = 'You can only query your own {}.'

class GetRefreshTokenByRedditor(Parameters):
    reddit_app_id = base_fields.Integer(required=True, description='Reddit app the Refresh Token is for')
    redditor = base_fields.String(required=True, description='Redditor the Refresh Token is for')

class CreateRefreshTokenParameters(PostFormParameters, schemas.BaseRefreshTokenSchema, validateOwner):
    reddit_app_id = base_fields.Integer(required=True, description='Reddit app the Refresh Token is for')
    redditor = base_fields.String(required=True, description='Redditor the Refresh Token is for')
    refresh_token = base_fields.String(required=True, description='The actual Refresh Token')
    scopes = base_fields.List(base_fields.String(description='Scope'), required=True, description='Scopes the Refresh Token grants access to')
    revoked = base_fields.Boolean(default=False, description='Indicates if the Refresh Token is revoked')

    class Meta(schemas.BaseRefreshTokenSchema.Meta):
        fields = schemas.BaseRefreshTokenSchema.Meta.fields

class PatchRefreshTokenDetailsParameters(PatchJSONParameters):
    '''
    Refresh Token details updating parameters following PATCH JSON RFC.
    '''
    fields = (RefreshToken.revoked.key,)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)