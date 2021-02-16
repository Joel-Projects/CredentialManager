from flask_login import current_user
from wtforms.fields import StringField
from wtforms_alchemy import InputRequired, URL, Unique

from app.extensions import ModelForm
from .models import RedditApp
from ...extensions.frontend.forms import (
    ModelSelectField,
    TextAreaFieldWithDefault,
    owners,
)


class RedditAppForm(ModelForm):
    class Meta:
        model = RedditApp
        only = [
            "app_name",
            "app_description",
            "client_id",
            "client_secret",
            "user_agent",
            "app_type",
            "redirect_uri",
            "enabled",
        ]
        fields = [
            "app_name",
            "app_description",
            ["client_id", "client_secret"],
            "user_agent",
            "app_type",
            "redirect_uri",
            "enabled",
        ]

    if current_user:
        userAgentDefault = current_user.getDefault("user_agent")  # pragma: no cover
    else:
        userAgentDefault = ""

    client_id = StringField(
        "Client ID",
        validators=[InputRequired(), Unique([RedditApp.client_id, RedditApp.owner])],
        description=RedditApp.client_id.info["description"],
    )
    user_agent = TextAreaFieldWithDefault(
        "User Agent",
        validators=[InputRequired()],
        default=userAgentDefault,
        description=RedditApp.user_agent.info["description"],
    )
    redirect_uri = StringField(
        "Redirect URI",
        validators=[URL(False)],
        default="https://credmgr.jesassn.org/oauth2/reddit_callback",
        description=RedditApp.redirect_uri.info["description"],
    )
    owner = ModelSelectField(
        query_factory=owners,
        queryKwargs={"current_user": current_user},
        default=current_user,
        description=RedditApp.owner_id.info["description"],
    )
