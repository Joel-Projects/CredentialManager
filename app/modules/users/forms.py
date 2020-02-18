from flask_login import current_user
from wtforms.fields import BooleanField, SubmitField, Field
from wtforms.meta import DefaultMeta
from wtforms.validators import Optional, url
from wtforms.widgets import HTMLString

from app.extensions import ModelForm
from .models import User
from ...extensions.frontend.forms import HiddenFieldWithToggle


class UserForm(ModelForm):
    class Meta:
        model = User
        only = ['username', 'password', 'reddit_username']

    is_admin = BooleanField('Admin?')
    is_internal = BooleanField('Internal?')
    is_regular_user = BooleanField('Regular User?')
    is_active = BooleanField('Active?')

    # submit = SubmitField('Create')
    # create_new = SubmitField('Create and New')

class EditUserForm(ModelForm):

    class Meta:
        model = User
        only = ['id', 'username', 'password', 'reddit_username']
        field_args = {
            'id': {'validators': [Optional()]},
            'password': {'validators': [Optional()]},
        }

    updatePassword = HiddenFieldWithToggle('Update Password?')
    is_admin = BooleanField('Admin?')
    is_internal = BooleanField('Internal?')
    is_regular_user = BooleanField('Regular User?')
    is_active = BooleanField('Active?')