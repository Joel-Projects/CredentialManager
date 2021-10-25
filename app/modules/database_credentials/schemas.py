from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema

from .models import DatabaseCredential


class BaseDatabaseCredentialSchema(ModelSchema):
    """
    Base Database Credential schema exposes only the most general fields.
    """

    owner_id = base_fields.Integer(
        description="Owner of the Database Credential. Requires Admin to create for other users."
    )

    class Meta:
        ordered = True
        model = DatabaseCredential
        fields = (
            DatabaseCredential.id.key,
            DatabaseCredential.app_name.key,
            DatabaseCredential.database_username.key,
            DatabaseCredential.database_host.key,
            DatabaseCredential.database.key,
            DatabaseCredential.database_flavor.key,
            DatabaseCredential.enabled.key,
            "resource_type",
        )
        dump_only = (DatabaseCredential.id.key, "resource_type")
        load_only = (DatabaseCredential.enabled.key,)

    _resource_type = Meta.model.__name__
    resource_type = base_fields.String(default=_resource_type)


class DetailedDatabaseCredentialSchema(BaseDatabaseCredentialSchema):
    """
    Detailed Database Credential schema exposes all useful fields.
    """

    class Meta(BaseDatabaseCredentialSchema.Meta):
        fields = BaseDatabaseCredentialSchema.Meta.fields + (
            DatabaseCredential.database_port.key,
            DatabaseCredential.database_password.key,
            DatabaseCredential.use_ssh.key,
            DatabaseCredential.ssh_host.key,
            DatabaseCredential.ssh_port.key,
            DatabaseCredential.ssh_username.key,
            DatabaseCredential.ssh_password.key,
            DatabaseCredential.use_ssh_key.key,
            DatabaseCredential.private_key.key,
            DatabaseCredential.private_key_passphrase.key,
            DatabaseCredential.owner_id.key,
        )
