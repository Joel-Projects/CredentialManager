from flask_login import current_user
from wtforms.fields import SubmitField, FormField, StringField
from app.extensions import ModelForm
from wtforms_alchemy import Length, QuerySelectField, Unique, InputRequired
from .models import SentryToken
from ..users.forms import UserForm
from ..users.models import User


def owners():
    return User.query


class SentryTokenForm(ModelForm):
    class Meta:
        model = SentryToken
        only = ['dsn']
    name = StringField('Name', validators=[InputRequired(), Unique([SentryToken.owner, SentryToken.name]), Length(3)])
    owner = QuerySelectField(query_factory=owners, default=current_user)