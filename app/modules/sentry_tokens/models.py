from sqlalchemy_utils import Timestamp

from app.extensions import db, InfoAttrs

class SentryToken(db.Model, Timestamp, InfoAttrs):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'sentry_tokens'
    _nameAttr = 'name'
    _enabledAttr = 'enabled'

    _infoAttrs = {
        'id': 'Sentry Token ID',
        'owner': 'Owner',
        'created': 'Created at',
        'updated': 'Last updated at'
    }

    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    dsn = db.Column(db.String, nullable=False, info={'label': 'DSN'})
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enabled'})
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))

    uniqueConstrant = db.UniqueConstraint(name, owner_id)

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user