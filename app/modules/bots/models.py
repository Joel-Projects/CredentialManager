from sqlalchemy_utils import Timestamp

from app.extensions import InfoAttrs, StrName, db, foreignKeyKwargs
from config import BaseConfig


class Bot(db.Model, Timestamp, InfoAttrs, StrName):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'bots'
    _displayNamePlural = 'Bots'
    _nameAttr = 'app_name'
    _enabledAttr = 'enabled'

    _infoAttrs = {
        'id': 'Bot ID',
        'owner': 'Owner',
        'created': 'Created at',
        'updated': 'Last updated at'
    }

    __table_args__ = {'schema': BaseConfig.SCHEMA_NAME}
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(length=50), nullable=False, info={'label': 'Bot Name'})
    reddit_app_id = db.Column(db.Integer, db.ForeignKey(f'{BaseConfig.SCHEMA_NAME}.reddit_apps.id', **foreignKeyKwargs), info={'label': 'Reddit App'})
    reddit_app = db.relationship('RedditApp', backref=db.backref(__tablename__, lazy='dynamic'), info={'label': 'Specifies the Reddit App that this bot will use.'})
    sentry_token_id = db.Column(db.Integer, db.ForeignKey(f'{BaseConfig.SCHEMA_NAME}.sentry_tokens.id', **foreignKeyKwargs), info={'label': 'Sentry Token'})
    sentry_token = db.relationship('SentryToken', backref=db.backref(__tablename__, lazy='dynamic'), info={'label': 'Specifies the Sentry Token that this bot will use.'})
    database_credential_id = db.Column(db.Integer, db.ForeignKey(f'{BaseConfig.SCHEMA_NAME}.database_credentials.id', **foreignKeyKwargs), info={'label': 'Database Credential'})
    database_credential = db.relationship('DatabaseCredential', backref=db.backref(__tablename__, lazy='dynamic'), info={'label': 'Specifies the Database Credential that this bot will use.'})
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enabled'})
    owner_id = db.Column(db.Integer, db.ForeignKey(f'{BaseConfig.SCHEMA_NAME}.users.id', ondelete='CASCADE', onupdate='CASCADE'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))

    uniqueConstraint = db.UniqueConstraint(app_name, owner_id)

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user