from flask_login import current_user
from wtforms import StringField
from wtforms.validators import InputRequired, Length
from wtforms_alchemy import Unique

from app.extensions import ModelForm
from .models import Bot
from ..reddit_apps.models import RedditApp
from ...extensions.frontend.forms import ModelSelectField, owners

def reddit_apps(owner):
    return owner.reddit_apps

def sentry_tokens(owner):
    return owner.sentry_tokens

def database_credentials(owner):
    return owner.database_credentials

class BotForm(ModelForm):
    class Meta:
        model = Bot
        only = ['app_name', 'enabled']

    app_name = StringField('Name', validators=[InputRequired(), Unique([Bot.owner, Bot.app_name]), Length(3)])
    owner = ModelSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user)
    reddit_app = ModelSelectField(query_factory=reddit_apps, queryKwargs={'owner': current_user}, allow_blank=True)
    sentry_token = ModelSelectField(query_factory=sentry_tokens, queryKwargs={'owner': current_user}, allow_blank=True)
    database_credential = ModelSelectField(query_factory=database_credentials, queryKwargs={'owner': current_user}, allow_blank=True)