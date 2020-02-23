from flask_login import current_user

from app.extensions import ModelForm
from wtforms_alchemy import QuerySelectField
from .models import Bot
from ..users.models import User
from ...extensions.frontend.forms import AppSelectField


def owners():
    return User.query

def reddit_apps(owner):
    return owner.reddit_apps

def sentry_tokens(owner):
    return owner.sentry_tokens

def database_credentials(owner):
    return owner.database_credentials

class EditBotForm(ModelForm):
    class Meta:
        model = Bot
        only = ['app_name', 'enabled']
    owner = QuerySelectField(query_factory=owners, default=current_user)
    reddit_app = AppSelectField(query_factory=reddit_apps, queryKwargs={'owner': current_user}, allow_blank=True)
    sentry_token = AppSelectField(query_factory=sentry_tokens, queryKwargs={'owner': current_user}, allow_blank=True)
    database_credential = AppSelectField(query_factory=database_credentials, queryKwargs={'owner': current_user}, allow_blank=True)

class BotForm(EditBotForm):
    pass