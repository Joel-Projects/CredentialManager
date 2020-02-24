import json, logging, requests
from datetime import datetime

from sqlalchemy_utils import ChoiceType
from app.extensions import db, InfoAttrs, StrName, foreignKeyKwargs

log = logging.getLogger(__name__)

class UserVerification(db.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'user_verifications'
    _nameAttr = 'discord_id'
    _enabledAttr = 'enabled'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reddit_app_id = db.Column(db.ForeignKey('credential_store.reddit_apps.id', **foreignKeyKwargs), nullable=False, info={'label': 'Reddit App', 'description': 'Reddit App the user will be verifying with'})
    reddit_app = db.relationship('RedditApp', primaryjoin='UserVerification.reddit_app_id == RedditApp.id', backref=__tablename__)
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'), info={'label': 'Owner', 'description': 'Owner of the verification.'})
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    discord_id = db.Column(db.BigInteger, unique=True, info={'label': "User's Dicord member ID ", 'description': 'Links reddit username to Discord member ID'})
    extra_data = db.Column(db.JSON, info={'label': 'Extra Data', 'description': 'Extra data linked to the verification'})
    redditor = db.Column(db.String, info={'label': 'Reddit Username', 'description': "The user's Reddit username"})
    verified_at = db.Column(db.DateTime(True))
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enable?', 'description': 'Allows the user verification to be used'})