from flask_marshmallow import base_fields
from flask_restplus_patched import PostFormParameters, PatchJSONParameters

from . import schemas
from .models import Bot


class CreateBotParameters(PostFormParameters, schemas.DetailedBotSchema):

    class Meta(schemas.DetailedBotSchema.Meta):
        pass


class PatchBotDetailsParameters(PatchJSONParameters):

    OPERATION_CHOICES = (PatchJSONParameters.OP_REPLACE,)

    PATH_CHOICES = tuple(f'/{field}' for field in (Bot.title.key,))
