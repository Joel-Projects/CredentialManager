import json

from flask_login import current_user
from wtforms import ValidationError
from wtforms.fields import TextAreaField

from app.extensions import ModelForm

from ...extensions.frontend.forms import ModelSelectField, owners, reddit_apps
from ..reddit_apps.models import RedditApp
from .models import UserVerification


class ExtraDataValidation(object):
    def __init__(self, message=None):
        if not message:
            message = "Invalid JSON payload."
        self.message = message

    def __call__(self, form, field):
        if field.data:
            try:
                data = json.loads(field.data)
                if not data:
                    raise ValidationError(self.message)

            except json.decoder.JSONDecodeError:
                raise ValidationError(self.message)


class RedditAppValidation(object):
    def __init__(self, message=None):
        if not message:
            message = "'You don't have the permission to create User Verifications with other users' Reddit Apps."
        self.message = message

    def __call__(self, form, field):
        if field.data:
            if (
                not current_user.is_admin
                and not current_user.is_internal
                and not field.data.owner == current_user
            ):
                raise ValidationError(self.message)


class UserVerificationForm(ModelForm):
    class Meta:
        model = UserVerification
        only = ["user_id", "redditor", "extra_data", "enabled"]
        fields = ["reddit_app", "user_id", "redditor", "extra_data"]

    reddit_app = ModelSelectField(
        query_factory=reddit_apps,
        queryKwargs={"owner": current_user},
        validators=[RedditAppValidation()],
        allow_blank=True,
    )
    owner = ModelSelectField(
        query_factory=owners,
        queryKwargs={"current_user": current_user},
        default=current_user,
        description=UserVerification.owner_id.info["description"],
    )
    extra_data = TextAreaField(validators=[ExtraDataValidation()])
