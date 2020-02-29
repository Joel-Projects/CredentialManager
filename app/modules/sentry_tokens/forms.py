from flask_login import current_user
from wtforms.fields import SubmitField, FormField, StringField
from wtforms.validators import URL

from app.extensions import ModelForm
from wtforms_alchemy import Length, Unique, InputRequired
from .models import SentryToken
from ...extensions.frontend.forms import AppSelectField, owners


class SentryTokenForm(ModelForm):
    class Meta:
        model = SentryToken
        only = ['dsn', 'enabled']
        field_args = {'enabled': {'default': True}}
    app_name = StringField('Name', validators=[InputRequired(), Unique([SentryToken.owner, SentryToken.app_name]), Length(3)])
    dsn = StringField('DSN', validators=[InputRequired(), URL()])
    owner = AppSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user)