import json, logging, requests
from datetime import datetime

from sqlalchemy_utils import ChoiceType
from app.extensions import db, InfoAttrs, StrName, foreignKeyKwargs

log = logging.getLogger(__name__)
class RefreshToken(db.Model, InfoAttrs, StrName):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'refresh_tokens'
    _nameAttr = 'app_name'
    _enabledAttr = 'enabled'
    _infoAttrs = {
        'id': 'Refresh Token ID',
        'app_name': 'App Name',
        'redditor': 'Redditor',
        'scopes': 'Authorized Scopes',
        'issued': 'Issued at'
    }
    scopeJSON = None
    try:
        response = requests.get('https://www.reddit.com/api/v1/scopes.json', headers={'User-Agent': 'python:flask scope checker by u/Lil_SpazJoekp'})
        scopeJSON = response.json()
    except Exception as error:
        log.exception(error)
    if not scopeJSON:
        with open('scopes.json', 'r') as f:
            scopeJSON = json.load(f)
    scopes = [(scope['id'], scope['name']) for scope in scopeJSON.values()]

    __table_args__ = {'schema': 'credential_store'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reddit_app_id = db.Column(db.ForeignKey('credential_store.reddit_apps.id', **foreignKeyKwargs), nullable=False, info={'label': 'Reddit App', 'description': 'Reddit App for users to authorize with'})
    reddit_app = db.relationship('RedditApp', primaryjoin='RefreshToken.reddit_app_id == RedditApp.id', backref='refresh_tokens')
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'), info={'label': 'Owner', 'description': 'Owner of the refresh token. Determines what Reddit Apps are displayed.'})
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    redditor = db.Column(db.String(22), nullable=False)
    refresh_token = db.Column(db.Text, unique=True, nullable=False)
    scopes = db.Column(ChoiceType(scopes))
    issued_at = db.Column(db.DateTime(True), default=datetime.astimezone(datetime.utcnow()), nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    revoked_at = db.Column(db.DateTime(True), default=datetime.astimezone(datetime.utcnow()), nullable=False)
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enable?', 'description': 'Allows the refresh token to be used'})

    uniqueConstrant = db.Index('only_one_active_token', reddit_app_id, redditor, revoked, unique=True, postgresql_where=(~revoked))

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user
