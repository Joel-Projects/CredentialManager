import base64, hashlib
from random import random
from sqlalchemy import func

from . import db
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata
foreignKeyKwargs = dict(ondelete='RESTRICT', onupdate='CASCADE')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    username = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean, server_default=db.text("false"))
    created = db.Column(db.DateTime(True), server_default=func.now())
    updated = db.Column(db.DateTime(True), server_default=func.now(), server_onupdate=func.current_timestamp())
    updated_by = db.Column(db.Text)
    enabled = db.Column(db.Boolean, server_default=db.text("true"))

class Bot(db.Model):
    __tablename__ = 'bots'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bot_name = db.Column(db.Text, unique=True)
    reddit = db.Column(db.Integer, db.ForeignKey('credential_store.reddit_apps.id', **foreignKeyKwargs))
    sentry = db.Column(db.Integer, db.ForeignKey('credential_store.sentry_tokens.id', **foreignKeyKwargs))
    owner = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', **foreignKeyKwargs))
    created = db.Column(db.DateTime(True), server_default=func.now())
    last_updated = db.Column(db.DateTime(True), server_default=func.now(), server_onupdate=func.current_timestamp())

    reddit_app = db.relationship('RedditApp', primaryjoin='Bot.reddit == RedditApp.id', backref='bots')
    sentry1 = db.relationship('Sentry', primaryjoin='Bot.sentry == Sentry.id', backref='bots')

class RedditApp(db.Model):
    __tablename__ = 'reddit_apps'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.Text, nullable=False, unique=True)
    shortname = db.Column(db.Text, unique=True)
    client_id = db.Column(db.Text, nullable=False)
    client_secret = db.Column(db.Text, nullable=False)
    user_agent = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)
    redirect_uri = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', **foreignKeyKwargs))
    state = db.Column(db.Text)
    created = db.Column(db.DateTime(True), server_default=func.now())

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    __table_args__ = {'schema': 'credential_store'}
    # __table_args__ = (, db.UniqueConstraint('refreshtoken', 'redditor', 'client_id', 'scopes'))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    redditor = db.Column(db.String(22), nullable=False)
    app_name = db.Column(db.ForeignKey('credential_store.reddit_apps.app_name', **foreignKeyKwargs), primary_key=True, nullable=False)
    app_id = db.Column(db.ForeignKey('credential_store.reddit_apps.id', **foreignKeyKwargs), primary_key=True, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    scopes = db.Column(db.ARRAY(db.Text()), nullable=False)
    issued = db.Column(db.DateTime(True), server_default=func.now())

    reddit_app = db.relationship('RedditApp', primaryjoin='RefreshToken.app_name == RedditApp.app_name', backref='refresh_tokens')

class Sentry(db.Model):
    __tablename__ = 'sentry_tokens'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.Text, unique=True)
    dsn = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', **foreignKeyKwargs))
    created = db.Column(db.DateTime(True), server_default=func.now())

class ApiToken(db.Model):
    __tablename__ = 'api_tokens'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True)
    token = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', **foreignKeyKwargs))
    created = db.Column(db.DateTime(True), server_default=func.now())

    def generate_token(self):
        base64.b64encode(hashlib.sha256(str(random.getrandbits(256))).digest(), random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')
