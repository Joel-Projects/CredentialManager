from flask_login import current_user
from wtforms.fields import SubmitField, FormField
from app.extensions import ModelForm
from wtforms_alchemy import ModelFieldList, QuerySelectField
from .models import SentryToken
from ..users.forms import UserForm
from ..users.models import User


def owners():
    return User.query


class SentryTokenForm(ModelForm):
    class Meta:
        model = SentryToken
    owner = QuerySelectField(query_factory=owners, default=current_user)