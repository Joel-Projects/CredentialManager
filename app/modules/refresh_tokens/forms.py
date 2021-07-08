from flask_login import current_user
from wtforms import BooleanField
from wtforms.validators import InputRequired

from app.extensions import ModelForm

from ...extensions.frontend.forms import ModelSelectField, owners
from .models import RefreshToken


def reddit_apps(owner):
    return owner.reddit_apps


def user_verifications(owner):
    return owner.user_verifications


class RefreshTokenForm(ModelForm):
    class Meta:
        item = RefreshToken
        fields = only = ["reddit_app_id", "owner"]
        field_args = {
            "reddit_app_id": {
                "validators": [InputRequired("You must select a Reddit App")]
            }
        }
        chunks = [
            [
                (scope, value["name"], value["description"])
                for scope, value in RefreshToken.scope_json.items()
            ][x : x + 3]
            for x in range(
                0,
                len(
                    [
                        (scope["id"], scope["name"], scope["description"])
                        for scope in RefreshToken.scope_json.values()
                    ]
                ),
                3,
            )
        ]

    reddit_app_id = ModelSelectField(
        query_factory=reddit_apps,
        query_kwargs={"owner": current_user},
        allow_blank=True,
        label="Reddit App",
    )
    user_verification_id = ModelSelectField(
        query_factory=user_verifications,
        query_kwargs={"owner": current_user},
        allow_blank=True,
        label="User Verification ID",
    )
    scopes = [
        (scope, value["name"], value["description"])
        for scope, value in Meta.item.scope_json.items()
    ]
    all = BooleanField("All Scopes", description="Check this to select all scopes")
    for id, name, description in scopes:
        Meta.fields.append(id)
        checked = False
        if id == "identity":
            checked = True
        locals()[id] = BooleanField(label=id, description=description, default=checked)
    owner = ModelSelectField(
        query_factory=owners,
        query_kwargs={"current_user": current_user},
        default=current_user,
        description=RefreshToken.owner_id.info["description"],
    )
