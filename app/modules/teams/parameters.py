"""
Input arguments (Parameters) for Team resources RESTful API
-----------------------------------------------------------
"""

from flask_marshmallow import base_fields
from flask_restplus_patched import PostFormParameters, PatchJSONParameters

from . import schemas
from .models import Team


class CreateTeamParameters(PostFormParameters, schemas.BaseTeamSchema):

    class Meta(schemas.BaseTeamSchema.Meta):
        pass


class PatchTeamDetailsParameters(PatchJSONParameters):

    OPERATION_CHOICES = (PatchJSONParameters.OP_REPLACE,)

    PATH_CHOICES = tuple(f'/{field}' for field in (Team.title.key,))


class AddTeamMemberParameters(PostFormParameters):
    user_id = base_fields.Integer(required=True)
