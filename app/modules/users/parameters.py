from flask_login import current_user
from flask_marshmallow import base_fields
from flask_restplus._http import HTTPStatus
from marshmallow import validates

from app.extensions.api import abort
from flask_restplus_patched import PatchJSONParameters, PostFormParameters
from . import permissions, schemas
from .models import User


class CreateUserParameters(PostFormParameters, schemas.BaseUserSchema):
    '''
    New user creation parameters.
    '''

    username = base_fields.String(description='Username for new user (Example: ```spaz```)', required=True)
    password = base_fields.String(description='Password for new user (Example: ```supersecurepassword```)', required=True)
    default_settings = base_fields.String(description='Default values to use for new apps (Example: ```{"database_flavor": "postgres", "database_host": "localhost"}```)', default={})
    is_active = base_fields.Boolean(description='Is the user active? Allows the user to sign in (Default: ``true``)', default=True)
    is_admin = base_fields.Boolean(description='Is the user an admin? Allows the user to see all objects and create users (Default: ``false``)', default=False)

    is_regular_user = base_fields.Boolean(description='(Internal use only)', default=True)
    is_internal = base_fields.Boolean(description='(Internal use only)', default=False)
    created = base_fields.LocalDateTime()

    @validates('is_internal')
    def validateInternal(self, data):
        if data:
            with permissions.InternalRolePermission():
                # Access granted
                pass

    class Meta(schemas.BaseUserSchema.Meta):
        fields = schemas.BaseUserSchema.Meta.fields + ('password', 'default_settings', 'is_admin', 'is_active', 'is_regular_user', 'is_internal', 'reddit_username')

class DeleteUserParameters(PostFormParameters, schemas.BaseUserSchema):
    user_id = base_fields.Integer(required=True)

class PatchUserDetailsParameters(PatchJSONParameters):
    '''
    User details updating parameters following PATCH JSON RFC.
    '''
    fields = (User.password.key, User.is_active.fget.__name__, User.is_regular_user.fget.__name__, User.is_internal.fget.__name__, User.is_admin.fget.__name__, User.default_settings.key, User.username.key, User.updated_by.key, User.reddit_username.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)

    @staticmethod
    def getPatchFields():
        fields = (User.password.key, User.default_settings.key, User.username.key, User.updated_by.key, User.reddit_username.key)
        if current_user.is_admin or current_user.is_internal:
            fields += (User.is_active.fget.__name__, User.is_admin.fget.__name__,)
        if current_user.is_internal:
            fields += (User.is_regular_user.fget.__name__, User.is_internal.fget.__name__,)
        return fields

    @classmethod
    def replace(cls, obj, field, value, state):
        '''
        Some fields require extra permissions to be changed.

        Changing `is_active`, `is_regular_user`, or `is_admin` property requires current user to be Admin.
        '''

        if current_user == obj:
            if field == User.is_active.fget.__name__:
                abort(code=HTTPStatus.NOT_ACCEPTABLE, message="You can't disable your own account.")
        if field in {User.is_active.fget.__name__, User.is_admin.fget.__name__}:
            permissions.AdminRolePermission().__enter__()

        if field in {User.is_internal.fget.__name__, User.is_regular_user.fget.__name__}:
            permissions.InternalRolePermission().__enter__()
        return super(PatchUserDetailsParameters, cls).replace(obj, field, value, state)
