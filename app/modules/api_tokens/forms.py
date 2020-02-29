from flask_login import current_user
from wtforms import SelectField, StringField
from wtforms_alchemy import QuerySelectField, InputRequired, Unique, Length

from app.extensions import ModelForm
from .models import ApiToken
from ...extensions.frontend.forms import owners, AppSelectField


class ApiTokenForm(ModelForm):
    class Meta:
        model = ApiToken
        only = ['enabled']

    name = StringField('Name', validators=[InputRequired(), Unique([ApiToken.owner, ApiToken.name]), Length(3)])
    length = SelectField('Legnth', choices=[('16', '16'), ('24', '24'), ('32', '32'), ('40', '40'), ('48', '48'), ('64', '64')], default='32', validators=None, description='How long you want the API token to be')
    owner = AppSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user)

class EditApiTokenForm(ModelForm):
    class Meta:
        model = ApiToken
        only = ['token', 'enabled']

    name = StringField('Name', validators=[InputRequired(), Unique([ApiToken.owner, ApiToken.name]), Length(3)])
    owner = AppSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user)
