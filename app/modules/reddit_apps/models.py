import base64
import hashlib
import logging

import praw
from flask_login import current_user
from sqlalchemy.event import listens_for
from sqlalchemy_utils import ChoiceType, URLType

from app.extensions import InfoAttrs, StrName, Timestamp, db
from config import BaseConfig

log = logging.getLogger(__name__)


class RedditApp(db.Model, Timestamp, InfoAttrs, StrName):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = "reddit_apps"
    _display_name_plural = "Reddit Apps"
    _name_attr = "app_name"
    _enabled_attr = "enabled"
    _info_attrs = {
        "id": "Reddit App ID",
        "app_type": "App Type",
        "owner": "Owner",
        "state": "State",
        "bots_using_app": "Bots using this",
        "refresh_tokens_count": "Refresh Tokens",
        "created": "Created at",
        "updated": "Last updated at",
    }

    __table_args__ = {"schema": BaseConfig.SCHEMA_NAME}

    reddit_app_types = [
        ("web", "Web App"),
        ("installed", "Installed App"),
        ("script", "Personal Use Script"),
    ]
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(
        db.String,
        nullable=False,
        info={"label": "App Name", "description": "Name of the Reddit App"},
    )
    app_description = db.Column(
        db.Text,
        info={"label": "Description", "description": "Description of the Reddit App"},
    )
    client_id = db.Column(
        db.String,
        nullable=False,
        info={"label": "Client ID", "description": "Client ID of the Reddit App"},
    )
    client_secret = db.Column(
        db.String,
        info={
            "label": "Client Secret",
            "description": "Client secret of the Reddit App",
        },
    )
    user_agent = db.Column(
        db.Text,
        nullable=False,
        info={
            "label": "User Agent",
            "description": "User agent used for requests to Reddit's API",
        },
    )
    app_type = db.Column(
        ChoiceType(reddit_app_types),
        nullable=False,
        info={
            "label": "App Type",
            "description": "Type of the app. One of `web`, `installed`, or `script`",
        },
    )
    redirect_uri = db.Column(
        URLType,
        default="https://credmgr.jesassn.org/oauth2/reddit_callback",
        nullable=False,
        info={
            "label": "Redirect URI",
            "description": "Redirect URI for Oauth2 flow. Defaults to `https://credmgr.jesassn.org/oauth2/reddit_callback`. Changing this will disable fetching of users' refresh tokens!",
        },
    )
    enabled = db.Column(
        db.Boolean,
        default=True,
        info={"label": "Enable?", "description": "Allows the app to be used"},
    )
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{BaseConfig.SCHEMA_NAME}.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        info={"label": "Owner", "description": "Owner of the Reddit App"},
    )
    owner = db.relationship("User", backref=db.backref(__tablename__, lazy="dynamic"))
    state = db.Column(db.String)
    unique_constraint = db.UniqueConstraint(client_id, owner_id)

    def check_owner(self, user):
        return self.owner == user

    @property
    def refresh_tokens_count(self):
        return len(self.refresh_tokens)

    @property
    def bots_using_app(self):
        from app.modules.bots.models import Bot

        return Bot.query.filter_by(reddit_app=self).count()

    def gen_auth_url(self, scopes, duration, user_verification=None):
        reddit = self.reddit_instance
        state = self.state
        if user_verification:
            state = base64.urlsafe_b64encode(f"{state}:{user_verification.user_id}".encode())
        return reddit.auth.url(scopes, state, duration)

    @classmethod
    def get_app_from_state(cls, state):
        user_id = None
        try:
            if state:
                result = cls.query.filter_by(state=state).first()
                if result:
                    return result, user_id
                else:
                    decoded = base64.urlsafe_b64decode(state).decode()
                    state, user_id = decoded.split(":")
                    result = cls.query.filter_by(state=state).first()
        except Exception as error:  # pragma: no cover
            log.exception(error)
        return result, user_id

    def get_refresh_token(self, redditor):
        if current_user.is_admin or current_user.is_internal:
            tokens = [i for i in self.refresh_tokens if i.redditor == redditor and not i.revoked]
        else:
            tokens = [
                i for i in self.refresh_tokens if i.redditor == redditor and not i.revoked and i.owner == current_user
            ]
        if tokens:
            return tokens[0]
        return None

    @property
    def reddit_instance(self) -> praw.Reddit.__class__:
        reddit_kwargs = ["client_id", "client_secret", "user_agent", "redirect_uri"]
        reddit = praw.Reddit(**{key: getattr(self, key) for key in reddit_kwargs})
        return reddit


@listens_for(RedditApp, "before_insert")
@listens_for(RedditApp, "before_update")
def update_state(mapper, connect, target):
    target.state = hashlib.sha256(target.client_id.encode()).digest().hex()
