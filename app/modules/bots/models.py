from sqlalchemy_utils import Timestamp

from app.extensions import InfoAttrs, StrName, db, foreignKeyKwargs


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

    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(length=50), nullable=False, info={'label': 'Bot Name'})
    reddit_id = db.Column(db.Integer, db.ForeignKey('credential_store.reddit_apps.id', **foreignKeyKwargs))
    reddit_app = db.relationship('RedditApp', backref=db.backref(__tablename__, lazy='dynamic'), info={'label': 'Specifies the Reddit App that this bot will use.'})
    sentry_id = db.Column(db.Integer, db.ForeignKey('credential_store.sentry_tokens.id', **foreignKeyKwargs))
    sentry_token = db.relationship('SentryToken', backref=db.backref(__tablename__, lazy='dynamic'), info={'label': 'Specifies the Sentry Token that this bot will use.'})
    database_id = db.Column(db.Integer, db.ForeignKey('credential_store.database_credentials.id', **foreignKeyKwargs))
    database_credential = db.relationship('DatabaseCredential', backref=db.backref(__tablename__, lazy='dynamic'), info={'label': 'Specifies the Database Credential that this bot will use.'})
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enabled'})
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))

    uniqueConstrant = db.UniqueConstraint(app_name, owner_id)

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user