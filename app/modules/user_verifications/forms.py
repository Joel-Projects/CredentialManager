from flask_login import current_user

from app.extensions import ModelForm
from .models import UserVerification
from ...extensions.frontend.forms import AppSelectField, owners


def reddit_apps(owner):
    return owner.reddit_apps

class UserVerificationForm(ModelForm):
    class Meta:
        model = UserVerification
        only = ['discord_id', 'redditor', 'extra_data', 'enabled']
        fields = ['reddit_app', 'discord_id', 'redditor', 'extra_data']
    reddit_app = AppSelectField(query_factory=reddit_apps, queryKwargs={'owner': current_user}, allow_blank=True)
    owner = AppSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user, description=UserVerification.owner_id.info['description'])