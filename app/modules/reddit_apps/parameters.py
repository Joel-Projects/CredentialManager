from flask_marshmallow import base_fields
from marshmallow import ValidationError, validates

from app.extensions.api.parameters import PaginationParameters, ValidateOwner
from flask_restplus_patched import PatchJSONParameters, PostFormParameters

from . import schemas
from .models import RedditApp


class ListRedditAppsParameters(PaginationParameters, ValidateOwner):
    owner_id = base_fields.Integer()

    class Meta:
        model = RedditApp

    invalid_owner_message = "You can only query your own {}."


class CreateRedditAppParameters(PostFormParameters, schemas.DetailedRedditAppSchema, ValidateOwner):
    app_name = base_fields.String(required=True, description="Name of the Reddit App")
    app_description = base_fields.String(description="Description of the Reddit App")
    client_id = base_fields.String(required=True, description="Client ID of the Reddit App")
    client_secret = base_fields.String(description="Client secret of the Reddit App")
    user_agent = base_fields.String(required=True, description="User agent used for requests to Reddit's API")
    app_type = base_fields.String(
        required=True,
        description="Type of the app. One of `web`, `installed`, or `script`",
    )
    redirect_uri = base_fields.Url(
        required=True,
        description="Redirect URI for Oauth2 flow. Defaults to user set redirect uri",
        default="https://credmgr.jesassn.org/oauth2/reddit_callback",
    )
    enabled = base_fields.Boolean(default=True, description="Allows the app to be used")

    @validates("app_name")
    def validate_name(self, data):
        if len(data) < 3:
            raise ValidationError("Name must be greater than 3 characters long.")

    @validates("app_type")
    def validate_app_type(self, data):
        if not data.lower() in ["web", "installed", "script"]:
            raise ValidationError("App type is not valid. Valid types are: 'web', 'installed'. or 'script'")


class PatchRedditAppDetailsParameters(PatchJSONParameters):
    """
    Reddit App details updating parameters following PATCH JSON RFC.
    """

    fields = (
        RedditApp.app_name.key,
        RedditApp.app_description.key,
        RedditApp.client_id.key,
        RedditApp.client_secret.key,
        RedditApp.user_agent.key,
        RedditApp.app_type.key,
        RedditApp.redirect_uri.key,
        RedditApp.enabled.key,
    )
    PATH_CHOICES = tuple(f"/{field}" for field in fields)


class GenerateAuthUrlParameters(PostFormParameters):
    user_verification_id = base_fields.Integer(
        description="Specify a User Verification ID to associate with the auth url by User Verification ID"
    )
    user_verification_user_id = base_fields.String(
        description="Specify a User Verification ID to associate with the auth url by User ID"
    )
    scopes = base_fields.List(
        base_fields.String(required=True),
        required=True,
        description="List of scopes needed for app",
    )
    duration = base_fields.String(
        default="permanent",
        description="Duration authorization is good for. Options are: `permanent` and `temporary`. Defaults to `permanent`.",
    )


class GetRefreshTokenByRedditor(PostFormParameters):
    redditor = base_fields.String(required=True, description="Redditor the Refresh Token is for")
