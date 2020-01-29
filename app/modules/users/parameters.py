# encoding: utf-8
# pylint: disable=wrong-import-order
"""
Input arguments (Parameters) for User resources RESTful API
-----------------------------------------------------------
"""

from flask_login import current_user
from flask_marshmallow import base_fields
from flask_restplus_patched import PostFormParameters, PatchJSONParameters
from flask_restplus._http import HTTPStatus
from marshmallow import validates, ValidationError

from app.extensions.api import abort

from . import schemas, permissions
from .models import User


class CreateUserParameters(PostFormParameters, schemas.BaseUserSchema):
    """
    New user creation parameters.
    """

    username = base_fields.String(description='Username for new user (Example: ```spaz```)', required=True)
    password = base_fields.String(description='Password for new user (Example: ```supersecurepassword```)', required=True)
    default_redirect_uri = base_fields.String(description='Default redirect uri to use for new reddit apps (Example: ```http://localhost:8080/callback```)', default='https://localhost:8080/callback')
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
        fields = schemas.BaseUserSchema.Meta.fields + ('password', 'default_redirect_uri', 'is_admin', 'is_active', 'is_regular_user', 'is_internal')

class DeleteUserParameters(PostFormParameters, schemas.BaseUserSchema):

    user_id = base_fields.Integer(required=True)

class PatchUserDetailsParameters(PatchJSONParameters):
  
    """
    User details updating parameters following PATCH JSON RFC.
    """
    fields = ('current_password', User.password.key, User.is_active.fget.__name__, User.is_regular_user.fget.__name__, User.is_admin.fget.__name__, 'default_redirect_uri', 'username')
    PATH_CHOICES = tuple(f'/{field}' for field in fields)

    @classmethod
    def test(cls, obj, field, value, state):
        """
        Additional check for 'current_password' as User hasn't field 'current_password'
        """
        if field == 'current_password':
            if current_user.password != value and obj.password != value:
                abort(code=HTTPStatus.FORBIDDEN, message="Wrong password")
            else:
                state['current_password'] = value
                return True
        return PatchJSONParameters.test(obj, field, value, state)

    @classmethod
    def replace(cls, obj, field, value, state):
        """
        Some fields require extra permissions to be changed.

        Changing `is_active`, `is_regular_user`, or `is_admin` property requires current user to be Admin, and
        `current_password` of the current user should be provided.
        """
        if 'current_password' not in state:
            raise ValidationError("Updating sensitive user settings requires `current_password` test operation performed before replacements.")

        if field in {User.is_active.fget.__name__, User.is_regular_user.fget.__name__, User.is_admin.fget.__name__}:
            with permissions.AdminRolePermission(password_required=True, password=state['current_password']):
                # Access granted
                pass
        if field == User.is_internal.fget.__name__:
            with permissions.InternalRolePermission(password_required=True, password=state['current_password']):
                # Access granted
                pass
        return super(PatchUserDetailsParameters, cls).replace(obj, field, value, state)
