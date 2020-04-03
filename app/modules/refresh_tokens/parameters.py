from flask_login import current_user
from flask_marshmallow import base_fields
from flask_restplus._http import HTTPStatus
from marshmallow import validates

from app.extensions.api.parameters import PaginationParameters, ValidateOwner
from flask_restplus_patched import PatchJSONParameters, PostFormParameters
from . import schemas
from .models import RefreshToken
from ..users import permissions


class ListRefreshTokensParameters(PaginationParameters, ValidateOwner):
    owner_id = base_fields.Integer()
    redditor = base_fields.String()

    class Meta:
        model = RefreshToken

    invalidOwnerMessage = 'You can only query your own {}.'

class GetRefreshTokenByRedditor(PostFormParameters):
    reddit_app_id = base_fields.Integer(required=True, description='Reddit app the Refresh Token is for')
    redditor = base_fields.String(required=True, description='Redditor the Refresh Token is for')

    @validates('reddit_app_id')
    def validateRedditApp(self, data):
        from ..reddit_apps.models import RedditApp
        redditApp = RedditApp.query.get_or_404(data)
        if redditApp.owner.is_internal:
            permissions.InternalRolePermission().__enter__()
        permissions.OwnerRolePermission(redditApp).__enter__()

class CreateRefreshTokenParameters(PostFormParameters, schemas.BaseRefreshTokenSchema, ValidateOwner):
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