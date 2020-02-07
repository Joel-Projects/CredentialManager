from flask_login import current_user
from wtforms import SelectField, StringField
from wtforms_alchemy import QuerySelectField, InputRequired, Unique, Length

from app.extensions import ModelForm
from .models import ApiToken
from ..users.models import User


def owners():
    if current_user.is_internal:
        return User.query
    else:
        users = User.query.all()
        return [user for user in users if not user.is_internal]


class ApiTokenForm(ModelForm):
    class Meta:
        model = ApiToken
        only = ['enabled']

    name = StringField('Name', validators=[InputRequired(), Unique([ApiToken.owner, ApiToken.name]), Length(3)])
    length = SelectField('Legnth', choices=[('16', '16'), ('24', '24'), ('32', '32'), ('40', '40'), ('48', '48'), ('64', '64')], default='32', validators=None, description='How long you want the API token to be')
    owner = QuerySelectField(query_factory=owners, default=current_user)