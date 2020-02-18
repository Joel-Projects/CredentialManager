from flask_login import current_user
from wtforms.compat import text_type

from app.extensions import ModelForm
from wtforms_alchemy import QuerySelectField
from .models import Bot
from ..database_credentials.models import DatabaseCredential
from ..reddit_apps.models import RedditApp
from ..sentry_tokens.models import SentryToken
from ..users.models import User


def owners():
    return User.query

def reddit_apps(owner):
    return owner.reddit_apps

def sentry_tokens(owner):
    return owner.sentry_tokens

def database_credentials(owner):
    return owner.database_credentials

class AppSelectField(QuerySelectField):

    def __init__(self, *, queryKwargs={}, **kwargs):
        self.queryKwargs = queryKwargs
        super().__init__(**kwargs)

    def _get_object_list(self):
        if self._object_list is None:
            query = (self.query if self.query is not None else self.query_factory(**self.queryKwargs))
            get_pk = self.get_pk
            self._object_list = list(
                (text_type(get_pk(obj)), obj) for obj in query
            )
        return self._object_list


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