from flask_login import current_user
from wtforms.fields import StringField
from wtforms_alchemy import URL, InputRequired, Unique

from app.extensions import ModelForm

from ...extensions.frontend.forms import ModelSelectField, TextAreaFieldWithDefault, owners
from .models import RedditApp


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
        user_agent_default = current_user.get_default("user_agent")  # pragma: no cover
    else:
        user_agent_default = ""

    client_id = StringField(
        "Client ID",
        validators=[InputRequired(), Unique([RedditApp.client_id, RedditApp.owner])],
        description=RedditApp.client_id.info["description"],
    )
    user_agent = TextAreaFieldWithDefault(
        "User Agent",
        validators=[InputRequired()],
        default=user_agent_default,
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
        query_kwargs={"current_user": current_user},
        default=current_user,
        description=RedditApp.owner_id.info["description"],
    )
