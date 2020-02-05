from flask_login import current_user
from flask_marshmallow import base_fields

from .models import Bot
from . import schemas
from flask_restplus_patched import PostFormParameters, PatchJSONParameters
from marshmallow import validates, ValidationError

from app.extensions.api.parameters import PaginationParameters, validateOwner

class ListBotsParameters(PaginationParameters, validateOwner):

    owner_id = base_fields.Integer()

    invalidOwnerMessage = 'You can only query your own {}.'

class CreateBotParameters(PostFormParameters, schemas.BaseBotSchema, validateOwner):
    name = base_fields.String(required=True, description='Name of the Bot')
    dsn = base_fields.String(required=True, description='DSN of the Bot')
    owner_id = base_fields.Integer(description='Owner of the token. Requires Admin to create for other users.')

    class Meta(schemas.BaseBotSchema.Meta):
        fields = schemas.BaseBotSchema.Meta.fields + ('owner_id',)

    @validates('name')
    def validateName(self, data):
        if len(data) < 3:
            raise ValidationError("Name must be greater than 3 characters long.")

class PatchBotDetailsParameters(PatchJSONParameters):
    """
    Bot details updating parameters following PATCH JSON RFC.
    """
    fields = (Bot.name.key, Bot.dsn.key)
    PATH_CHOICES = tuple(f'/{field}' for field in fields)
