import sqlalchemy
from sqlalchemy_utils import ChoiceType, URLType

from app.extensions import db, InfoAttrs, Timestamp

class RedditApp(db.Model, Timestamp, InfoAttrs):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'reddit_apps'
    _nameAttr = 'app_name'
    _enabledAttr = 'enabled'
    _infoAttrs = {
        'id': 'Reddit App ID',
        'owner': 'Owner',
        'state': 'State',
        'created': 'Created at',
        'updated': 'Last updated at'
    }

    __table_args__ = {'schema': 'credential_store'}

    redditAppTypes = [('web', 'Web App'), ('installed', 'Installed App'), ('script', 'Personal Use Script')]
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String, nullable=False, info={'label': 'App Name', 'description': 'Name of the Reddit App'})
    short_name = db.Column(db.String, info={'label': 'Short Name', 'description': 'Short name of the Reddit App'})
    app_description = db.Column(db.Text, info={'label': 'Description', 'description': 'Description of the Reddit App'})
    client_id = db.Column(db.String, nullable=False, info={'label': 'Client ID', 'description': 'Client ID of the Reddit App'})
    client_secret = db.Column(db.String, nullable=False, info={'label': 'Client Secret', 'description': 'Client secret of the Reddit App'})
    user_agent = db.Column(db.Text, nullable=False, info={'label': 'User Agent', 'description': 'User agent used for requests to Reddit\'s API'})
    app_type = db.Column(ChoiceType(redditAppTypes), nullable=False, info={'label': 'App Type', 'description': 'Type of the app. One of `web`, `installed`, or `script`'})
    redirect_uri = db.Column(URLType, default='https://credmgr.jesassn.org/oauth2/reddit_callback', nullable=False, info={'label': 'Redirect URI', 'description': 'Redirect URI for Oauth2 flow. Defaults to `https://credmgr.jesassn.org/oauth2/reddit_callback`. Changing this will disable fetching of users\' refresh tokens!'})
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enable?', 'description': 'Allows the app to be used'})
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'), info={'label': 'Owner', 'description': 'Owner of the Reddit App'})
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    state = db.Column(db.String)
    uniqueConstrant = db.UniqueConstraint(client_id, owner_id)

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user

# @sqlalchemy.event.listens_for(RedditApp, 'before_update', propagate=True)
# def timestamp_before_update(mapper, connection, target):
#     # When a model with a timestamp is updated; force update the updated
#     # timestamp.
#     target.state = datetime.astimezone(datetime.utcnow())