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
            Bot.bot_name.key,
            Bot.reddit_id.key,
            Bot.sentry_id.key,
            Bot.database_id.key,
            Bot.owner_id.key,
            Bot.enabled.key
        )
        dump_only = (
            Bot.id.key,
            Bot.bot_name.key,
            Bot.reddit_id.key,
            Bot.sentry_id.key,
            Bot.database_id.key,
            Bot.owner_id.key,
            Bot.enabled.key
        )


class DetailedBotSchema(BaseBotSchema):
    """
    Detailed Bot schema exposes all useful fields.
    """

    class Meta(BaseBotSchema.Meta):
        fields = BaseBotSchema.Meta.fields + (
            Bot.created.key,
            Bot.updated.key,
        )
        dump_only = BaseBotSchema.Meta.dump_only + (
            Bot.created.key,
            Bot.updated.key,
        )
