# encoding: utf-8
"""
User database models
--------------------
"""
import enum
from datetime import datetime

from sqlalchemy_utils import types as column_types, Timestamp
from flask_login import UserMixin
from app.extensions import db
from app.modules.api_tokens.models import ApiToken

def getStaticRole(roleName, staticRole):
    """
    A helper function that aims to provide a property getter and setter
    for static roles.

    Args:
        roleName (str)
        staticRole (int) - a bit mask for a specific role
    """
    @property
    def isStaticRole(self):
        return self.hasStaticRole(staticRole)

    @isStaticRole.setter
    def isStaticRole(self, value):
        if value:
            self.setStaticRole(staticRole)
        else:
            self.unsetStaticRole(staticRole)

    isStaticRole.fget.__name__ = roleName
    return isStaticRole


class User(db.Model, Timestamp, UserMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'users'
    _nameAttr = 'username'
    _enabledAttr = 'is_active'

    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=80), unique=True, nullable=False, info={'label': 'Username'})
    password = db.Column(column_types.PasswordType(max_length=128, schemes=('bcrypt',)), nullable=False, info={'label': 'Password'})
    default_redirect_uri = db.Column(db.Text, default='http://localhost:8080', info={'label': 'Default Redirect URI'})
    created_by = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='SET NULL', onupdate='CASCADE'))
    updated_by = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='SET NULL', onupdate='CASCADE'))

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

    is_internal = getStaticRole('is_internal', StaticRoles.INTERNAL)
    is_admin = getStaticRole('is_admin', StaticRoles.ADMIN)
    is_regular_user = getStaticRole('is_regular_user', StaticRoles.REGULAR_USER)
    is_active = getStaticRole('is_active', StaticRoles.ACTIVE)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, username="{self.username}", is_admin={self.is_admin}, is_active={self.is_active})>'

    def __str__(self):
        return self.username

    def hasStaticRole(self, role):
        return (self.static_roles & role.mask) != 0

    def setStaticRole(self, role):
        if self.hasStaticRole(role):
            return
        self.static_roles |= role.mask

    def unsetStaticRole(self, role):
        if not self.hasStaticRole(role):
            return
        self.static_roles ^= role.mask

    def check_owner(self, user):
        return self == user

    @classmethod
    def findWithPassword(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if not user:
            return None
        if user.password == password:
            return user
        return None

    @classmethod
    def findWithApiKey(cls, apiKey):
        apiToken = ApiToken.query.filter_by(token=apiKey).first()
        if not apiToken:
            return None
        user = cls.query.filter_by(id=apiToken.owner_id).first()
        if user:
            apiToken.last_used = datetime.now()
            return user
        return None
