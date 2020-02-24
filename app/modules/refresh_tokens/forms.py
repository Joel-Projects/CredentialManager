from flask_login import current_user
from wtforms import BooleanField
from wtforms.validators import InputRequired
from wtforms_alchemy import QuerySelectField

from app.extensions import ModelForm
from .models import RefreshToken
from ..users.models import User
from ...extensions.frontend.forms import AppSelectField

def owners():
    return User.query

def reddit_apps(owner):
    return owner.reddit_apps

class GenerateRefreshTokenForm(ModelForm):
    class Meta:
        item = RefreshToken
        fields = only = ['reddit_app_id', 'owner']
        field_args = {'reddit_app_id': {'validators': [InputRequired('You must select a Reddit App')]}}
        chunks = [[(scope['id'], scope['name'], scope['description']) for scope in RefreshToken.scopeJSON.values()][x:x+3] for x in range(0, len([(scope['id'], scope['name'], scope['description']) for scope in RefreshToken.scopeJSON.values()]), 3)]
    reddit_app_id = AppSelectField(query_factory=reddit_apps, queryKwargs={'owner': current_user}, allow_blank=True)
    scopes = [(scope['id'], scope['name'], scope['description']) for scope in Meta.item.scopeJSON.values()]
    all = BooleanField('All Scopes', description='Check this to select all scopes')
    for id, name, description in scopes:
        Meta.fields.append(id)
        checked = False
        if id == 'identity':
            checked = True
        locals()[id] = BooleanField(label=id, description=description, default=checked)
    owner = QuerySelectField(query_factory=owners, default=current_user, description=RefreshToken.owner_id.info['description'])