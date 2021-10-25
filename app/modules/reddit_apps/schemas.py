from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema, fields

from .models import RedditApp


class BaseRedditAppSchema(ModelSchema):
    """
    Base Reddit App schema exposes only the most general fields.
    """

    owner_id = base_fields.Integer(description="Owner of the Reddit App. Requires Admin to create for other users.")

    class Meta:
        ordered = True
        model = RedditApp
        fields = (
            RedditApp.id.key,
            RedditApp.app_name.key,
            RedditApp.client_id.key,
            RedditApp.client_secret.key,
            RedditApp.enabled.key,
            "resource_type",
        )
        dump_only = (RedditApp.id.key, "resource_type")
        load_only = (RedditApp.enabled.key,)

    _resource_type = Meta.model.__name__
    resource_type = base_fields.String(default=_resource_type)


class DetailedRedditAppSchema(BaseRedditAppSchema):
    """
    Detailed Reddit App schema exposes all useful fields.
    """

    class Meta(BaseRedditAppSchema.Meta):

        fields = BaseRedditAppSchema.Meta.fields + (
            RedditApp.app_description.key,
            RedditApp.user_agent.key,
            RedditApp.app_type.key,
            RedditApp.redirect_uri.key,
            RedditApp.state.key,
            RedditApp.owner_id.key,
        )
        dump_only = BaseRedditAppSchema.Meta.dump_only + (RedditApp.state.key,)

    app_type = base_fields.String(
        description="Type of the app. One of `web`, `installed`, or `script`",
        attribute="app_type.code",
    )


class AuthUrlSchema(BaseRedditAppSchema):
    """
    Detailed Reddit App schema exposes all useful fields.
    """

    class Meta(BaseRedditAppSchema.Meta):
        fields = (
            RedditApp.id.key,
            RedditApp.app_name.key,
            RedditApp.client_id.key,
            "auth_url",
            "resource_type",
        )
