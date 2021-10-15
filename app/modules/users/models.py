import enum
import json
import logging
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy_utils import types as column_types

from app.extensions import InfoAttrs, QueryProperty, StrName, Timestamp, cache, db
from app.extensions.api import abort
from app.modules.api_tokens.models import ApiToken
from config import BaseConfig

log = logging.getLogger(__name__)


def get_static_role(role_name, static_role):
    """
    A helper function that aims to provide a property getter and setter
    for static roles.

    Args:
        role_name (str)
        static_role (int) - a bit mask for a specific role
    """

    @property
    def is_static_role(self):
        return self.has_static_role(static_role)

    @is_static_role.setter
    def is_static_role(self, value):
        if value:
            self.set_static_role(static_role)
        else:
            self.unset_static_role(static_role)

    is_static_role.fget.__name__ = role_name
    return is_static_role


class User(db.Model, Timestamp, UserMixin, InfoAttrs, StrName, QueryProperty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = "users"
    _display_name_plural = "Users"
    _name_attr = "username"
    _enabled_attr = "is_active"
    _info_attrs = {
        "id": "User ID",
        "_created_by.username": "Created By",
        "_updated_by.username": "Updated By",
        "bots.count": "Bots",
        "database_credentials.count": "Database Credentials",
        "reddit_apps.count": "Reddit Apps",
        "refresh_tokens.count": "Authenticated Users",
        "sentry_tokens.count": "Sentry Tokens",
        "api_tokens.count": "API Tokens",
    }

    __table_args__ = {"schema": BaseConfig.SCHEMA_NAME}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=80), unique=True, nullable=False, info={"label": "Username"})
    password = db.Column(
        column_types.PasswordType(max_length=128, schemes=("bcrypt",)),
        nullable=False,
        info={"label": "Password"},
    )
    default_settings = {"database_flavor": "postgres", "database_host": "localhost"}
    default_settings = db.Column(
        db.JSON,
        server_default=json.dumps(default_settings),
        default=default_settings,
        info={"label": "Default Settings"},
    )
    reddit_username = db.Column(db.String, info={"label": "Reddit Username"})
    sentry_auth_token = db.Column(db.String, info={"label": "Sentry Auth Token"})
    created_by = db.Column(
        db.Integer,
        db.ForeignKey(
            f"{BaseConfig.SCHEMA_NAME}.users.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )
    _created_by = db.relationship("User", remote_side=id, foreign_keys=[created_by])
    updated_by = db.Column(
        db.Integer,
        db.ForeignKey(
            f"{BaseConfig.SCHEMA_NAME}.users.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )
    _updated_by = db.relationship("User", remote_side=id, foreign_keys=[updated_by])
    internal = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)

    class StaticRoles(enum.Enum):
        INTERNAL = (0x8000, "Internal")
        ADMIN = (0x4000, "Admin")
        REGULAR_USER = (0x2000, "Regular User")
        ACTIVE = (0x1000, "Active Account")

        @property
        def mask(self):
            return self.value[0]

        @property
        def title(self):
            return self.value[1]

    static_roles = db.Column(db.Integer, default=0, nullable=False)

    is_internal = get_static_role("is_internal", StaticRoles.INTERNAL)
    is_admin = get_static_role("is_admin", StaticRoles.ADMIN)
    is_regular_user = get_static_role("is_regular_user", StaticRoles.REGULAR_USER)
    is_active = get_static_role("is_active", StaticRoles.ACTIVE)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, username="{self.username}", is_admin={self.is_admin}, is_active={self.is_active})>'

    def has_static_role(self, role):
        return (self.static_roles & role.mask) != 0

    def set_static_role(self, role):
        if self.has_static_role(role):
            return
        self.static_roles |= role.mask
        if role.title == "Internal":
            self.internal = True
        if role.title == "Admin":
            self.admin = True

    def unset_static_role(self, role):
        if not self.has_static_role(role):
            return
        self.static_roles ^= role.mask
        if role.title == "Internal":
            self.internal = False
        if role.title == "Admin":
            self.admin = False

    def check_owner(self, user):
        return self == user

    def get_default(self, setting):
        default = self.default_settings.get(setting, "")
        if not default and setting == "redirect_uri":
            default = "https://credmgr.jesassn.org/oauth2/reddit_callback"
        return default

    @classmethod
    def find_with_password(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if not user:
            return None
        if user.password == password:
            return user
        return None

    @classmethod
    def find_with_api_token(cls, api_token):
        user_id, api_token_id = cls.get_user_id(api_token)
        log.info("find_with_api_token: hitting database")
        user = cls.query.filter_by(id=user_id).first()
        if user:
            with db.session.begin():
                ApiToken(id=api_token_id).last_used = datetime.now()
            return user

    @classmethod
    @cache.memoize(timeout=1800)
    def get_user_id(cls, api_token):
        log.info("get_user_id: hitting database")
        api_token = ApiToken.query.filter_by(token=api_token).first()
        if not api_token.enabled:
            abort(401, "API Token invalid or disabled")
        return api_token.owner_id, api_token.id
