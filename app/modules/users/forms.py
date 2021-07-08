from wtforms.fields import BooleanField
from wtforms.validators import Optional

from app.extensions import ModelForm

from ...extensions.frontend.forms import HiddenFieldWithToggle
from .models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        only = ["username", "password", "reddit_username", "sentry_auth_token"]

    is_admin = BooleanField("Admin?")
    is_internal = BooleanField("Internal?")
    is_regular_user = BooleanField("Regular User?")
    is_active = BooleanField("Active?")


class EditUserForm(ModelForm):
    class Meta:
        model = User
        only = ["id", "username", "password", "reddit_username", "sentry_auth_token"]
        field_args = {
            "id": {"validators": [Optional()]},
            "password": {"validators": [Optional()]},
        }

    update_password = HiddenFieldWithToggle("Update Password?")
    is_admin = BooleanField("Admin?")
    is_internal = BooleanField("Internal?")
    is_regular_user = BooleanField("Regular User?")
    is_active = BooleanField("Active?")
