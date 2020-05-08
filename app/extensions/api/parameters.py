import json
from http import HTTPStatus

from flask_login import current_user
from marshmallow import validate, validates, ValidationError

from flask_marshmallow import base_fields

from app.extensions.api import http_exceptions
from app.modules.users import permissions
from app.modules.users.models import User
from flask_restplus_patched import Parameters


class PaginationParameters(Parameters):
    limit = base_fields.Integer(
        description='limit a number of items (allowed range is 1-100), default is 20.',
        missing=20,
        validate=validate.Range(min=1, max=100)
    )
    offset = base_fields.Integer(
        description='a number of items to skip, default is 0.',
        missing=0,
        validate=validate.Range(min=0)
    )

def validateOwnerExists(user_id: int) -> User:
    return User.query.get(user_id)

class ValidateOwner(Parameters):
    owner_id_attr = 'owner_id'

    invalidOwnerMessage = "You don't have the permission to create {} for other users."

    @validates(owner_id_attr)
    def validateOwnerId(self, data):
        item = validateOwnerExists(data)
        if item:
            if item.is_internal: # pragma: no cover
                permissions.InternalRolePermission().__enter__()
            if current_user.id != data and not (current_user.is_admin or current_user.is_internal):
                raise http_exceptions.abort(HTTPStatus.FORBIDDEN, self.invalidOwnerMessage.format(self.Meta.model._displayNamePlural))
        else:
            raise ValidationError("That user doesn't exist")

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