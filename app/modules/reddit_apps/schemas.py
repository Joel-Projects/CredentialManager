from flask_restplus_patched import ModelSchema
from .models import RedditApp


class BaseRedditAppSchema(ModelSchema):
    '''
    Base Reddit App schema exposes only the most general fields.
    '''

    class Meta:
        ordered = True
        model = RedditApp
        fields = (
            RedditApp.id.key,
            RedditApp.app_name.key,
            RedditApp.client_id.key,
            RedditApp.client_secret.key
        )
        dump_only = (
            RedditApp.id.key,
        )

class DetailedRedditAppSchema(BaseRedditAppSchema):
    '''
    Detailed Reddit App schema exposes all useful fields.
    '''

    class Meta(BaseRedditAppSchema.Meta):
        fields = BaseRedditAppSchema.Meta.fields + (
            RedditApp.short_name.key,
            RedditApp.app_description.key,
            RedditApp.user_agent.key,
            RedditApp.app_type.key,
            RedditApp.redirect_uri.key,
            RedditApp.state.key,
            RedditApp.enabled.key,
            RedditApp.owner_id.key
        )

class RedditAppBotSchema(BaseRedditAppSchema):
    '''
    Reddit App Bot schema exposes all useful fields for Bots.
    '''

    class Meta:
        ordered = True
        model = RedditApp
        fields = (
            RedditApp.id.key,
            RedditApp.app_name.key,
            RedditApp.client_id.key,
            RedditApp.client_secret.key,
            RedditApp.user_agent.key,
            RedditApp.redirect_uri.key
        )

class AuthUrlSchema(BaseRedditAppSchema):
    '''
    Detailed Reddit App schema exposes all useful fields.
    '''

    class Meta(BaseRedditAppSchema.Meta):
        fields = (RedditApp.id.key, RedditApp.app_name.key, RedditApp.client_id.key, 'auth_url')