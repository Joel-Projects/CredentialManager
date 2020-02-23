from flask_login import current_user
from flask_marshmallow import base_fields

from .models import RedditApp
from . import schemas
from flask_restplus_patched import PostFormParameters, PatchJSONParameters
from marshmallow import validates, ValidationError

from app.extensions.api.parameters import PaginationParameters, validateOwner

class ListRedditAppsParameters(PaginationParameters, validateOwner):

    owner_id = base_fields.Integer()

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateRedditAppParameters(PostFormParameters, schemas.BaseRedditAppSchema, validateOwner):
    reddit_app = base_fields.String(required=True, description='Name of the Reddit App')
    short_name = base_fields.String(description='Short name of the Reddit App')
    app_description = base_fields.String(description='Description of the Reddit App')
    client_id = base_fields.String(required=True, description='Client ID of the Reddit App')
    client_secret = base_fields.String(description='Client secret of the Reddit App')
    user_agent = base_fields.String(required=True, description='User agent used for requests to Reddit\'s API')
    app_type = base_fields.String(required=True, description='Type of the app. One of `web`, `installed`, or `script`')
    redirect_uri = base_fields.String(required=True, description='Redirect URI for Oauth2 flow. Defaults to user set redirect uri')
    enabled = base_fields.String(default=True, description='Allows the app to be used')
    owner_id = base_fields.Integer(description='Owner of the app. Requires Admin to create for other users.')

    class Meta(schemas.BaseRedditAppSchema.Meta):
        fields = schemas.BaseRedditAppSchema.Meta.fields + ('owner_id',)

    @validates('app_name')
    def validateName(self, data):
        if len(data) < 3:
            raise ValidationError("Name must be greater than 3 characters long.")

    @validates('app_type')
    def validateAppType(self, data):
        if not data.lower() in ['web', 'installed', 'script']:
            raise ValidationError("App type is not valid. Valid types are: 'web', 'installed'. or 'script'`")

class PatchRedditAppDetailsParameters(PatchJSONParameters):
    """
    Reddit App details updating parameters following PATCH JSON RFC.
    """
    fields = (
        RedditApp.app_name.key,
        RedditApp.short_name.key,
        RedditApp.app_description.key,
        RedditApp.client_id.key,
        RedditApp.client_secret.key,
        RedditApp.user_agent.key,
        RedditApp.app_type.key,
        RedditApp.redirect_uri.key,
        RedditApp.enabled.key
    )
    PATH_CHOICES = tuple(f'/{field}' for field in fields)

class GenerateAuthUrlParameters(PostFormParameters):

    scopes = base_fields.List(base_fields.String(required=True), required=True)
    duration = base_fields.String(required=True)
    state = base_fields.String()

    invalidOwnerMessage = 'You can only query your own {}.'
