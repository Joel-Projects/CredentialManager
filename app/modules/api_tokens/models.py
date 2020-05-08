import random

from app.extensions import InfoAttrs, Timestamp, db
from config import BaseConfig


class ApiToken(db.Model, Timestamp, InfoAttrs):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'api_tokens'
    _nameAttr = 'name'
    _displayNamePlural = 'API Tokens'
    _enabledAttr = 'enabled'
    _infoAttrs = {
        'id': 'API Token ID',
        'owner': 'Owner',
        'created': 'Created at',
        'updated': 'Last updated at',
        'last_used': 'Last Used'
    }

    __table_args__ = {'schema': BaseConfig.SCHEMA_NAME}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, info={'label': 'Name'})
    token = db.Column(db.String, nullable=False, info={'label': 'API Token'})
    length = db.Column(db.Integer, db.CheckConstraint('length BETWEEN 16 AND 128'), nullable=False, info={'label': 'Length'}, default=32)
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enabled'})
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    last_used = db.Column(db.DateTime(True))

    unique = db.UniqueConstraint(name, owner_id)

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user

    @staticmethod
    def generate_token(length=32):
        '''genToken = lambda: base64.b64encode(hashlib.sha256(str(random.getrandbits(256)).encode()).digest(), random.choice([b'rA', b'aZ', b'gQ', b'hH', b'hG', b'aR', b'DD'])).rstrip(b'==').decode()
        self.token = ''.join([''.join(list(i)) for i in zip(genToken(), genToken())])[:length]
        '''
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-~'
        return "".join(random.choice(characters) for _ in range(length))