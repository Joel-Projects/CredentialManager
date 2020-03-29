from flask_marshmallow import base_fields
from marshmallow import ValidationError, validates

from app.extensions.api.parameters import PaginationParameters, ValidateOwner
from flask_restplus_patched import PatchJSONParameters, PostFormParameters
from . import schemas
from .models import DatabaseCredential


class ListDatabaseCredentialsParameters(PaginationParameters, ValidateOwner):
    owner_id = base_fields.Integer()

    class Meta:
        model = DatabaseCredential

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateDatabaseCredentialParameters(PostFormParameters, schemas.BaseDatabaseCredentialSchema, ValidateOwner):
    app_name = base_fields.String(required=True, description='Name of the Database Credential')
    database_flavor = base_fields.String(default='postgres', required=True, description='Type of database, defaults to `postgres`')
    database = base_fields.String(default='postgres', description='Working database to use, defaults to `postgres`')
    database_host = base_fields.String(default='localhost', required=True, description='Database server address, defaults to `localhost`')
    database_port = base_fields.Integer(default=5432, required=True, description='Port the database server listens on, defaults to `5432`')
    database_username = base_fields.String(required=True, description='Username to use to connect to the database')
    database_password = base_fields.String(required=True, description='Password to use to connect to the database')
    use_ssh = base_fields.Boolean(default=False, description='Determines if the database will be connected to through a tunnel')
    ssh_host = base_fields.String(description='The address of the server that the SSH tunnel will connect to')
    ssh_port = base_fields.Integer(description='The port the SSH tunnel will use')
    ssh_username = base_fields.String(description='Username for the SSH tunnel')
    ssh_password = base_fields.String(description='Password for the SSH tunnel')
    use_ssh_key = base_fields.Boolean(default=False, description='Allows the credentials to be used')
    private_key = base_fields.String(description='SSH private key. Note: No validation will be performed.')
    private_key_passphrase = base_fields.String(description='Passphrase for the SSH key')
    enabled = base_fields.Boolean(default=True, description='Allows the credentials to be used')
    owner_id = base_fields.Integer(description='Owner of the app. Requires Admin to create for other users.')

    class Meta(schemas.BaseDatabaseCredentialSchema.Meta):
        fields = schemas.BaseDatabaseCredentialSchema.Meta.fields + ('owner_id',)

    @validates('app_name')
    def validateName(self, data):
        if len(data) < 3:
            raise ValidationError('Name must be greater than 3 characters long.')

class PatchDatabaseCredentialDetailsParameters(PatchJSONParameters):
    '''
    Database Credential details updating parameters following PATCH JSON RFC.
    '''
    fields = (
        DatabaseCredential.app_name.key,
        DatabaseCredential.database_flavor.key,
        DatabaseCredential.database.key,
        DatabaseCredential.database_host.key,
        DatabaseCredential.database_port.key,
        DatabaseCredential.database_username.key,
        DatabaseCredential.database_password.key,
        DatabaseCredential.use_ssh.key,
        DatabaseCredential.ssh_host.key,
        DatabaseCredential.ssh_port.key,
        DatabaseCredential.ssh_username.key,
        DatabaseCredential.ssh_password.key,
        DatabaseCredential.use_ssh_key.key,
        DatabaseCredential.private_key.key,
        DatabaseCredential.private_key_passphrase.key,
        DatabaseCredential.enabled.key
    )
    PATH_CHOICES = tuple(f'/{field}' for field in fields)