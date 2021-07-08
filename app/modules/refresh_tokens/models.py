import json
import logging
from datetime import datetime, timezone

import requests

from app.extensions import InfoAttrs, StrName, db
from config import BaseConfig

log = logging.getLogger(__name__)


class RefreshToken(db.Model, InfoAttrs, StrName):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = "refresh_tokens"
    _display_name_plural = "Refresh Tokens"
    _name_attr = "redditor"
    _info_attrs = {
        "id": "Refresh Token ID",
        "reddit_app": "Reddit App",
        "redditor": "Redditor",
        "owner": "Owner",
        "refresh_token": "Refresh Token",
        "scopes": "Authorized Scopes",
        "issued_at": "Issued at",
        "revoked_at": "Revoked at",
        "updated": "Last updated at",
    }
    scope_json = None
    try:
        response = requests.get(
            "https://www.reddit.com/api/v1/scopes.json",
            headers={"User-Agent": "python:flask scope checker by u/Lil_SpazJoekp"},
        )
        scope_json = response.json()
    except Exception as error:  # pragma: no cover
        log.exception(error)
    if not scope_json:
        with open("scopes.json", "r") as f:  # pragma: no cover
            scope_json = json.load(f)

    __table_args__ = {"schema": BaseConfig.SCHEMA_NAME}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reddit_app_id = db.Column(
        db.ForeignKey(
            f"{BaseConfig.SCHEMA_NAME}.reddit_apps.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        info={
            "label": "Reddit App",
            "description": "Reddit App for users to authorize with",
        },
    )
    reddit_app = db.relationship(
        "RedditApp",
        primaryjoin="RefreshToken.reddit_app_id == RedditApp.id",
        backref="refresh_tokens",
    )
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey(
            f"{BaseConfig.SCHEMA_NAME}.users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        info={
            "label": "Owner",
            "description": "Owner of the refresh token. Determines what Reddit Apps are displayed.",
        },
    )
    owner = db.relationship("User", backref=db.backref(__tablename__, lazy="dynamic"))
    redditor = db.Column(db.String(22), nullable=False)
    refresh_token = db.Column(db.Text, unique=True, nullable=False)
    scopes = db.Column(db.JSON, default=[])
    issued_at = db.Column(db.DateTime(True), default=datetime.utcnow(), nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    revoked_at = db.Column(db.DateTime(True))
    updated = db.Column(
        db.DateTime(True),
        default=datetime.astimezone(datetime.utcnow()),
        nullable=False,
    )

    unique_constraint = db.Index(
        "only_one_active_token",
        reddit_app_id,
        redditor,
        revoked,
        unique=True,
        postgresql_where=(~revoked),
    )

    def check_owner(self, user):
        return self.owner == user

    def revoke(self):
        self.revoked = True
        self.revoked_at = datetime.now(timezone.utc)

    @property
    def app_name(self):
        return self.reddit_app.app_name

    @property
    def valid(self):
        return not self.revoked

    @property
    def chunk_scopes(self):
        scopes = [
            (scope, scope in self.scopes, value["description"])
            for scope, value in self.scope_json.items()
        ]
        return [scopes[x : x + 4] for x in range(0, len(scopes), 4)]
