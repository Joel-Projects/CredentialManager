from flask_login import current_user
from wtforms.fields import SubmitField, TextAreaField, StringField
from app.extensions import ModelForm
from wtforms_alchemy import Length, QuerySelectField, Unique, InputRequired, URL
from .models import RedditApp
from ..users.models import User
from ...extensions.frontend.forms import TextAreaFieldWithDefault


def owners():
    return User.query

class EditRedditAppForm(ModelForm):
    class Meta:
        model = RedditApp
        only = ['app_name', 'short_name', 'app_description', 'client_id', 'client_secret', 'user_agent', 'app_type', 'redirect_uri', 'enabled']
        fields = [['app_name', 'short_name'], 'app_description', ['client_id', 'client_secret'], 'user_agent', 'app_type', 'redirect_uri', 'enabled']
    if current_user:
        userAgentDefault = current_user.getDefault('user_agent')
        redirectUriDefault = current_user.getDefault('redirect_uri')
    else:
        userAgentDefault = ''
        redirectUriDefault = ''
    user_agent = TextAreaFieldWithDefault('User Agent', validators=[InputRequired()], default=userAgentDefault, description=RedditApp.user_agent.info['description'])
    redirect_uri = StringField('Redirect URI', validators=[URL(False)], default=redirectUriDefault, description=RedditApp.redirect_uri.info['description'])
    owner = QuerySelectField(query_factory=owners, default=current_user, description=RedditApp.owner_id.info['description'])

class RedditAppForm(EditRedditAppForm):
    pass

