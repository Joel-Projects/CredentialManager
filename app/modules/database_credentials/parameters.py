from flask_login import current_user
from flask_marshmallow import base_fields

from .models import DatabaseCredential
from . import schemas
from flask_restplus_patched import PostFormParameters, PatchJSONParameters
from marshmallow import validates, ValidationError

from app.extensions.api.parameters import PaginationParameters, validateOwner

class ListDatabaseCredentialsParameters(PaginationParameters, validateOwner):

    owner_id = base_fields.Integer()

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateDatabaseCredentialParameters(PostFormParameters, schemas.BaseDatabaseCredentialSchema, validateOwner):
    app_name = base_fields.String(required=True, description='Name of the Database Credential')
    database_flavor = base_fields.String(required=True, description='Client ID of the Database Credential')
    database_host = base_fields.String(required=True, description='Client ID of the Database Credential')
    database_port = base_fields.String(required=True, description='Client ID of the Database Credential')
    database_username = base_fields.String(required=True, description='Client ID of the Database Credential')
    database_password = base_fields.String(required=True, description='Client ID of the Database Credential')
    database = base_fields.String(description='Client secret of the Database Credential')
    ssh = base_fields.String(required=True, description='User agent used for requests to Reddit\'s API')
    ssh_host = base_fields.String(required=True, description='Type of the app. One of `web`, `installed`, or `script`')
    ssh_port = base_fields.String(required=True, description='Type of the app. One of `web`, `installed`, or `script`')
    ssh_username = base_fields.String(required=True, description='Redirect URI for Oauth2 flow. Defaults to user set redirect uri')
    ssh_password = base_fields.String(required=True, description='Redirect URI for Oauth2 flow. Defaults to user set redirect uri')
    ssh_key = base_fields.String(required=True, description='Redirect URI for Oauth2 flow. Defaults to user set redirect uri')
    private_key = base_fields.String(required=True, description='Redirect URI for Oauth2 flow. Defaults to user set redirect uri')
    enabled = base_fields.Boolean(default=True, description='Allows the app to be used')
    owner_id = base_fields.Integer(description='Owner of the app. Requires Admin to create for other users.')

    class Meta(schemas.BaseDatabaseCredentialSchema.Meta):
        fields = schemas.BaseDatabaseCredentialSchema.Meta.fields + ('owner_id',)

    @validates('app_name')
    def validateName(self, data):
        if len(data) < 3:
            raise ValidationError("Name must be greater than 3 characters long.")

    @validates('app_type')
    def validateAppType(self, data):
        if not data.lower() in ['web', 'installed', 'script']:
            raise ValidationError("App type is not valid. Valid types are: 'web', 'installed'. or 'script'`")

class PatchDatabaseCredentialDetailsParameters(PatchJSONParameters):
    """
    Database Credential details updating parameters following PATCH JSON RFC.
    """
    fields = (
        DatabaseCredential.app_name.key,
        DatabaseCredential.short_name.key,
        DatabaseCredential.app_description.key,
        DatabaseCredential.client_id.key,
        DatabaseCredential.client_secret.key,
        DatabaseCredential.user_agent.key,
        DatabaseCredential.app_type.key,
        DatabaseCredential.redirect_uri.key,
        DatabaseCredential.enabled.key
    )
    PATH_CHOICES = tuple(f'/{field}' for field in fields)
