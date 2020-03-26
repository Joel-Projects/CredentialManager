import json

from flask_login import current_user
from wtforms import ValidationError
from wtforms.fields import TextAreaField
from app.extensions import ModelForm
from .models import UserVerification
from ...extensions.frontend.forms import AppSelectField, TextArea, owners


def reddit_apps(owner):
    return owner.reddit_apps

class ExtraDataValidation(object):
    def __init__(self, message=None):
        if not message:
            message = 'Invalid JSON payload.'
        self.message = message

    def __call__(self, form, field):
        if field.data:
            try:
                data = json.loads(field.data)
                if not data:
                    raise ValidationError(self.message)

            except json.decoder.JSONDecodeError:
                raise ValidationError(self.message)



class UserVerificationForm(ModelForm):
    class Meta:
        model = UserVerification
        only = ['discord_id', 'redditor', 'extra_data', 'enabled']
        fields = ['reddit_app', 'discord_id', 'redditor', 'extra_data']

    reddit_app = AppSelectField(query_factory=reddit_apps, queryKwargs={'owner': current_user}, allow_blank=True)
    owner = AppSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user, description=UserVerification.owner_id.info['description'])
    extra_data = TextAreaField(validators=[ExtraDataValidation()])