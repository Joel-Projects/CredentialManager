import base64, hashlib
from random import random
from sqlalchemy import func
from sqlalchemy_utils import URLType, ChoiceType, PasswordType

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
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    default_redirect_uri = db.Column(db.Text, default='http://localhost:8080')
    admin = db.Column(db.Boolean, default=db.text("false"))
    enabled = db.Column(db.Boolean, default=db.text("true"))
    created = db.Column(db.DateTime(True), default=func.now())
    created_by = db.Column(db.Text)
    updated = db.Column(db.DateTime(True), default=func.now(), onupdate=func.current_timestamp(), server_default=func.now(), server_onupdate=func.current_timestamp())
    updated_by = db.Column(db.Text)

class Bot(db.Model):
    __tablename__ = 'bots'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bot_name = db.Column(db.Text, unique=True)
    reddit_id = db.Column(db.Integer, db.ForeignKey('credential_store.reddit_apps.id', **foreignKeyKwargs))
    reddit = db.relationship('RedditApp', backref=db.backref(__tablename__, lazy='dynamic'))
    sentry_id = db.Column(db.Integer, db.ForeignKey('credential_store.sentry_tokens.id', **foreignKeyKwargs))
    sentry = db.relationship('Sentry', backref=db.backref(__tablename__, lazy='dynamic'))
    database_id = db.Column(db.Integer, db.ForeignKey('credential_store.database_credentials.id', **foreignKeyKwargs))
    database = db.relationship('Database', backref=db.backref(__tablename__, lazy='dynamic'))
    enabled = db.Column(db.Boolean, default=db.text("true"))
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    created = db.Column(db.DateTime(True), default=func.now(), server_default=func.now())
    last_updated = db.Column(db.DateTime(True), default=func.now(), onupdate=func.current_timestamp(), server_default=func.now(), server_onupdate=func.current_timestamp())

class RedditApp(db.Model):
    __tablename__ = 'reddit_apps'
    __table_args__ = {'schema': 'credential_store'}
    redditAppTypes = [('web', 'Web App'), ('installed', 'Installed App'), ('script', 'Personal User Script')]
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String, nullable=False, unique=True, info={'label': 'App Name'})
    short_name = db.Column(db.String, unique=True, info={'label': 'Short Name'})
    app_description = db.Column(db.Text, info={'label': 'Description'})
    client_id = db.Column(db.String, nullable=False, info={'label': 'Client ID'})
    client_secret = db.Column(db.String, nullable=False, info={'label': 'Client Secret'})
    user_agent = db.Column(db.Text, nullable=False, info={'label': 'User Agent'})
    app_type = db.Column(ChoiceType(redditAppTypes), nullable=False, info={'label': 'App Type'})
    redirect_uri = db.Column(URLType, nullable=False, info={'label': 'Redirect URI'})
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enable?'})
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    state = db.Column(db.String)
    created = db.Column(db.DateTime(True), default=func.now(), server_default=func.now())

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    __table_args__ = {'schema': 'credential_store'}
    # __table_args__ = (, db.UniqueConstraint('refreshtoken', 'redditor', 'client_id', 'scopes'))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reddit_app = db.relationship('RedditApp', primaryjoin='RefreshToken.app_name == RedditApp.app_name', backref='refresh_tokens')
    redditor = db.Column(db.String(22), nullable=False)
    app_name = db.Column(db.ForeignKey('credential_store.reddit_apps.app_name', **foreignKeyKwargs), primary_key=True, nullable=False)
    app_id = db.Column(db.ForeignKey('credential_store.reddit_apps.id', **foreignKeyKwargs), primary_key=True, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    scopes = db.Column(db.ARRAY(db.Text()), nullable=False)
    issued = db.Column(db.DateTime(True), default=func.now(), server_default=func.now())

class Sentry(db.Model):
    __tablename__ = 'sentry_tokens'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String, unique=True, info={'label': 'App Name'})
    dsn = db.Column(URLType, nullable=False, info={'label': 'DSN'})
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    created = db.Column(db.DateTime(True), default=func.now(), server_default=func.now())

class Database(db.Model):
    __tablename__ = 'database_credentials'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String, unique=True, info={'label': 'DB Name'})
    database_flavor = db.Column(db.String, nullable=False, default='postgres', info={'label': 'DB Kind'})
    database_host = db.Column(db.String, nullable=False, default='localhost', info={'label': 'DB Host'})
    database_port = db.Column(db.Integer, nullable=False, default=5432, info={'label': 'DB Port'})
    database_username = db.Column(db.String, nullable=False, info={'label': 'DB Username'})
    database_password = db.Column(db.String, nullable=False, info={'label': 'DB Password'})
    database = db.Column(db.String, nullable=False, default='postgres', info={'label': 'Database'})
    ssh = db.Column(db.Boolean, default=False, info={'label': 'SSH?'})
    ssh_host = db.Column(db.String, info={'label': 'SSH Host'})
    ssh_port = db.Column(db.Integer, info={'label': 'SSH Port'})
    ssh_username = db.Column(db.String, info={'label': 'SSH Username'})
    ssh_password = db.Column(db.String, info={'label': 'SSH Password'})
    private_key = db.Column(db.Text, info={'label': 'Private Key'})
    private_key_passphrase = db.Column(db.String, info={'label': 'Private Key Passphrase'})
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    created = db.Column(db.DateTime(True), default=func.now(), server_default=func.now())

class ApiToken(db.Model):
    __tablename__ = 'api_tokens'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    token = db.Column(db.String, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    created = db.Column(db.DateTime(True), default=func.now(), server_default=func.now())

    def generate_token(self):
        self.token = base64.b64encode(hashlib.sha256(str(random.getrandbits(256)).encode()).digest(), random.choice([b'rA', b'aZ', b'gQ', b'hH', b'hG', b'aR', b'DD'])).rstrip(b'==').decode()