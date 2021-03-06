import logging
from datetime import datetime

from app.extensions import InfoAttrs, db, foreign_key_kwargs
from config import BaseConfig

log = logging.getLogger(__name__)


class UserVerification(db.Model, InfoAttrs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = "user_verifications"
    _display_name_plural = "User Verifications"
    _name_attr = "user_id"
    _enabled_attr = "enabled"

    _info_attrs = {
        "id": "User Verification ID",
        "owner": "Owner",
        "verified_at": "Verified at",
        "created": "Created at",
    }

    __table_args__ = {"schema": BaseConfig.SCHEMA_NAME}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reddit_app_id = db.Column(
        db.ForeignKey(f"{BaseConfig.SCHEMA_NAME}.reddit_apps.id", **foreign_key_kwargs),
        info={
            "label": "Reddit App",
            "description": "Reddit App the user will be verifying with",
        },
    )
    reddit_app = db.relationship(
        "RedditApp",
        primaryjoin="UserVerification.reddit_app_id == RedditApp.id",
        backref=__tablename__,
    )
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{BaseConfig.SCHEMA_NAME}.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        info={"label": "Owner", "description": "Owner of the verification."},
    )
    owner = db.relationship("User", backref=db.backref(__tablename__, lazy="dynamic"))
    user_id = db.Column(
        db.String,
        nullable=False,
        unique=True,
        info={
            "label": "User's unique ID",
            "description": "Links reddit username to an unique ID",
        },
    )
    extra_data = db.Column(
        db.JSON,
        info={
            "label": "Extra Data",
            "description": "Extra JSON data linked to the verification",
        },
    )
    redditor = db.Column(
        db.String,
        info={
            "label": "Reddit Username",
            "description": "The user's Reddit username. Note: This is not usually set manually.",
        },
    )
    verified_at = db.Column(db.DateTime(True))
    enabled = db.Column(
        db.Boolean,
        default=True,
        info={
            "label": "Enable?",
            "description": "Allows the user verification to be used",
        },
    )
    created = db.Column(
        db.DateTime(True),
        default=datetime.astimezone(datetime.utcnow()),
        nullable=False,
    )

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user

    def __str__(self):  # pragma: no cover
        redditor = ""
        if self.redditor:
            redditor = f" - {self.redditor}"
        return f"{self.user_id}{redditor}"
