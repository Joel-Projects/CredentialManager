import sqlalchemy
from sqlalchemy_utils import ChoiceType, URLType

from app.extensions import db, InfoAttrs, Timestamp

class DatabaseCredential(db.Model, Timestamp, InfoAttrs):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'database_credentials'
    _nameAttr = 'app_name'
    _enabledAttr = 'enabled'
    _infoAttrs = {
        'id': 'Database Credential ID',
        'owner': 'Owner',
        'created': 'Created at',
        'updated': 'Last updated at'
    }

    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String, unique=True, info={'label': 'DB Name'})
    database_flavor = db.Column(db.String, nullable=False, default='postgres', info={'label': 'DB Kind'})
    database_host = db.Column(db.String, nullable=False, default='localhost', info={'label': 'DB Host'})
    database_port = db.Column(db.Integer, nullable=False, default=5432, info={'label': 'DB Port'})
    database_username = db.Column(db.String, nullable=False, info={'label': 'DB Username'})
    database_password = db.Column(db.String, info={'label': 'DB Password'})
    database = db.Column(db.String, nullable=False, default='postgres', info={'label': 'Database'})
    ssh = db.Column(db.Boolean, default=False, info={'label': 'SSH?'})
    ssh_host = db.Column(db.String, info={'label': 'SSH Host'})
    ssh_port = db.Column(db.Integer, info={'label': 'SSH Port'})
    ssh_username = db.Column(db.String, info={'label': 'SSH Username'})
    ssh_password = db.Column(db.String, info={'label': 'SSH Password'})
    ssh_key = db.Column(db.Boolean, info={'label': 'Use SSH Key?'})
    private_key = db.Column(db.Text, info={'label': 'Private Key'})
    private_key_passphrase = db.Column(db.String, info={'label': 'Private Key Passphrase'})
    enabled = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    uniqueConstrant = db.UniqueConstraint(app_name, owner_id)

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user