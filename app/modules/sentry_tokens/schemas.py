from flask_restplus_patched import ModelSchema

from .models import SentryToken


class BaseSentryTokenSchema(ModelSchema):
    '''
    Base Sentry Token schema exposes only the most general fields.
    '''

    class Meta:
        ordered = True
        model = SentryToken
        fields = (
            SentryToken.id.key,
            SentryToken.app_name.key,
            SentryToken.dsn.key,
            SentryToken.enabled.key
        )
        dump_only = (
            SentryToken.id.key,
        )

class DetailedSentryTokenSchema(BaseSentryTokenSchema):
    '''
    Detailed Sentry Token schema exposes all useful fields.
    '''

    class Meta(BaseSentryTokenSchema.Meta):
        fields = BaseSentryTokenSchema.Meta.fields + (
            SentryToken.owner_id.key,
            SentryToken.created.key
        )

class SentryTokenBotSchema(BaseSentryTokenSchema):
    '''
    Sentry Token Bot schema exposes all useful fields for Bots.
    '''

    class Meta:
        ordered = True
        model = SentryToken
        fields = (
            SentryToken.id.key,
            SentryToken.app_name.key,
            SentryToken.dsn.key
        )