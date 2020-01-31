from flask_login import current_user
from wtforms.fields import BooleanField, SubmitField
from app.extensions import ModelForm
from .models import User


class UserForm(ModelForm):
    class Meta:
        model = User

    admin = BooleanField('Admin?')
    internal = BooleanField('Internal?')
    active = BooleanField('Active?')

    submit = SubmitField('Create')
    # create_new = SubmitField('Create and New')