import itertools

from flask_login import current_user
from wtforms import SelectField, StringField
from wtforms_alchemy import InputRequired, Length, Unique

from app.extensions import ModelForm

from ...extensions.frontend.forms import ModelSelectField, owners
from .models import ApiToken


class ApiTokenForm(ModelForm):
    class Meta:
        model = ApiToken
        only = ["enabled"]

    name = StringField(
        "Name",
        validators=[
            InputRequired(),
            Unique([ApiToken.owner, ApiToken.name]),
            Length(3),
        ],
    )
    length = SelectField(
        "Length",
        choices=[(i, str(i)) for i in itertools.chain(range(16, 56, 8), [64])],
        default="32",
        validators=None,
        description="How long you want the API token to be",
        coerce=int,
    )
    owner = ModelSelectField(
        query_factory=owners,
        query_kwargs={"current_user": current_user},
        default=current_user,
    )


class EditApiTokenForm(ModelForm):
    class Meta:
        model = ApiToken
        only = ["token", "enabled"]

    name = StringField(
        "Name",
        validators=[
            InputRequired(),
            Unique([ApiToken.owner, ApiToken.name]),
            Length(3),
        ],
    )
    owner = ModelSelectField(
        query_factory=owners,
        query_kwargs={"current_user": current_user},
        default=current_user,
    )
