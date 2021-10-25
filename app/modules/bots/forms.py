from flask_login import current_user
from wtforms import StringField
from wtforms.validators import InputRequired, Length
from wtforms_alchemy import Unique

from app.extensions import ModelForm

from ...extensions.frontend.forms import ModelSelectField, check_model_owner, owners
from .models import Bot


def reddit_apps(owner):
    owner = check_model_owner(owner)
    return owner.reddit_apps.filter_by(enabled=True)


def sentry_tokens(owner):
    owner = check_model_owner(owner)
    return owner.sentry_tokens.filter_by(enabled=True)


def database_credentials(owner):
    owner = check_model_owner(owner)
    return owner.database_credentials.filter_by(enabled=True)


class BotForm(ModelForm):
    class Meta:
        model = Bot
        only = ["app_name", "enabled"]

    app_name = StringField(
        "Name",
        validators=[InputRequired(), Unique([Bot.owner, Bot.app_name]), Length(3)],
    )
    owner = ModelSelectField(
        query_factory=owners,
        query_kwargs={"current_user": current_user},
        default=current_user,
    )
    reddit_app = ModelSelectField(
        query_factory=reddit_apps,
        query_kwargs={"owner": current_user},
        allow_blank=True,
        label="Reddit App",
    )
    sentry_token = ModelSelectField(
        query_factory=sentry_tokens,
        query_kwargs={"owner": current_user},
        allow_blank=True,
        label="Sentry Token",
    )
    database_credential = ModelSelectField(
        query_factory=database_credentials,
        query_kwargs={"owner": current_user},
        allow_blank=True,
        label="Database Credential",
    )
