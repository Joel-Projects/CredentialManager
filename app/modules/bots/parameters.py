from flask_marshmallow import base_fields
from marshmallow import ValidationError, validates

from app.extensions.api.parameters import PaginationParameters, ValidateOwner
from flask_restplus_patched import Parameters, PatchJSONParameters, PostFormParameters
from . import schemas
from .models import Bot


class ListBotsParameters(PaginationParameters, ValidateOwner):
    owner_id = base_fields.Integer(
        description="Filter by owner of the bot. Requires Admin to get for other users."
    )

    class Meta:
        model = Bot

    invalidOwnerMessage = "You can only query your own {}."


class GetBotByName(PostFormParameters, ValidateOwner):
    app_name = base_fields.String(required=True, description="Name of the Bot")
    owner_id = base_fields.Integer(
        description="Owner of the bot. Requires Admin to get for other users."
    )

    class Meta:
        model = Bot


class CreateBotParameters(PostFormParameters, schemas.DetailedBotSchema, ValidateOwner):
    app_name = base_fields.String(required=True, description="Name of the Bot")
    reddit_app_id = base_fields.Integer(description="Reddit App the bot will use")
    sentry_token_id = base_fields.Integer(description="Sentry Token the bot will use")
    database_credential_id = base_fields.Integer(
        description="Database Credential the bot will use"
    )

    class Meta(schemas.DetailedBotSchema.Meta):
        fields = (
            "app_name",
            "reddit_app_id",
            "sentry_token_id",
            "database_credential_id",
            "owner_id",
        )

    @validates("app_name")
    def validateName(self, data):
        if len(data) < 3:
            raise ValidationError("Name must be greater than 3 characters long.")


class PatchBotDetailsParameters(PatchJSONParameters):
    fields = (
        Bot.app_name.key,
        "reddit_app_id",
        "sentry_token_id",
        "database_credential_id",
        Bot.enabled.key,
    )
    PATH_CHOICES = tuple(f"/{field}" for field in fields)
