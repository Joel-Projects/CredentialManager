from flask_marshmallow import base_fields
from flask_restplus_patched import ModelSchema

from .models import Bot


class BaseBotSchema(ModelSchema):
    """
    Base Bot schema exposes only the most general fields.
    """
    class Meta:
        model = Bot
        fields = (
            Bot.id.key,
            Bot.name.key,
            Bot.dsn.key
        )


class DetailedBotSchema(BaseBotSchema):
    """
    Detailed Bot schema exposes all useful fields.
    """

    class Meta(BaseBotSchema.Meta):
        fields = BaseBotSchema.Meta.fields + (
            Bot.owner_id.key,
            Bot.created.key,
        )
