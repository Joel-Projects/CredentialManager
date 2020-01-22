import base64, hashlib
from random import random
from sqlalchemy_utils import Timestamp

from app.extensions import db

class ApiToken(db.Model, Timestamp):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'api_tokens'
    # __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, primary_key=True)
    token = db.Column(db.String, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    # owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='restrict', onupdate='CASCADE'))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='restrict', onupdate='CASCADE'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    last_used = db.Column(db.DateTime(True))

    __table_args__ = (
        db.UniqueConstraint(name, owner_id),
    )

    def check_owner(self, user):
        return self.owner == user

    def generate_token(self):
        self.token = base64.b64encode(hashlib.sha256(str(random.getrandbits(256)).encode()).digest(), random.choice([b'rA', b'aZ', b'gQ', b'hH', b'hG', b'aR', b'DD'])).rstrip(b'==').decode()
