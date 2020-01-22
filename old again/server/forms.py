# from wtforms import SubmitField

from . import db
from .models import User, Bot, RedditApp, Sentry, Database, ApiToken
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class UserForm(ModelForm):
    class Meta:
        model = User

    # create = SubmitField('Create')
    # create_new = SubmitField('Create and New')


class BotForm(ModelForm):
    class Meta:
        model = Bot

    # create = SubmitField('Create')
    # create_new = SubmitField('Create and New')


class RedditAppForm(ModelForm):
    class Meta:
        model = RedditApp
        only = ['app_name', 'short_name', 'app_description', 'client_id', 'client_secret', 'user_agent', 'app_type', 'redirect_uri', 'enabled']

    # add = SubmitField('Add')
    # add_new = SubmitField('Add and New')

class SentryForm(ModelForm):
    class Meta:
        model = Sentry

    # add = SubmitField('Add')
    # add_new = SubmitField('Add and New')

class DatabaseForm(ModelForm):
    class Meta:
        model = Database

    # add = SubmitField('Add')
    # add_new = SubmitField('Add and New')

class ApiTokenForm(ModelForm):
    class Meta:
        model = ApiToken

    # create = SubmitField('Create')
    # create_new = SubmitField('Create and New')
forms = {'userForm': UserForm, 'botForm': BotForm, 'redditAppForm': RedditAppForm, 'sentryForm': SentryForm, 'databaseForm': DatabaseForm, 'apiTokenForm': ApiTokenForm}