from app.extensions import InfoAttrs, StrName, Timestamp, db
from config import BaseConfig


class DatabaseCredential(db.Model, Timestamp, InfoAttrs, StrName):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'database_credentials'
    _nameAttr = 'app_name'
    _displayNamePlural = 'Database Credentials'
    _enabledAttr = 'enabled'
    _infoAttrs = {
        'id': 'Database Credential ID',
        'owner': 'Owner',
        'botsUsingApp': 'Bots using this',
        'created': 'Created at',
        'updated': 'Last updated at'
    }

    __table_args__ = {'schema': BaseConfig.SCHEMA_NAME}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String, nullable=False, info={'label': 'Database Name'})
    database_flavor = db.Column(db.String, nullable=False, default='postgres', info={'label': 'Database Kind', 'description': 'Mostly for infomational purposes. Defaults to \'postgres\'. Can be set in user defaults.'})
    database_host = db.Column(db.String, nullable=False, default='localhost', info={'label': 'Database Host', 'description': 'Hostname of the server for the database. Defaults to \'localhost\'. Can be set in user defaults.'})
    database_port = db.Column(db.Integer, nullable=False, default=5432, info={'label': 'Database Port', 'description': 'Port to use to connect to the database. Defaults to \'5432\'.'})
    database_username = db.Column(db.String, nullable=False, info={'label': 'Database Username'})
    database_password = db.Column(db.String, info={'label': 'Database Password'})
    database = db.Column(db.String, nullable=False, default='postgres', info={'label': 'Working Database', 'description': 'Main database to use. Defaults to \'postgres\'.'})
    use_ssh = db.Column(db.Boolean, default=False, server_default='false', info={'label': 'SSH?', 'description': 'Check this to use a SSH tunnel to connect to the database server.'})
    ssh_host = db.Column(db.String, info={'label': 'SSH Host', 'description': ''})
    ssh_port = db.Column(db.Integer, default=22, info={'label': 'SSH Port', 'description': 'Port for the SSH tunnel. Defaults to \'22\''})
    ssh_username = db.Column(db.String, info={'label': 'SSH Username', 'description': 'Username to use for the SSH tunnel. Required if not using a SSH key.'})
    ssh_password = db.Column(db.String, info={'label': 'SSH Password', 'description': 'Password to use for the SSH tunnel. Required if not using a SSH key.'})
    use_ssh_key = db.Column(db.Boolean, default=False, server_default='false', info={'label': 'Use SSH Key?', 'description': 'Check this to use a SSH key to connect to the database server.'})
    private_key = db.Column(db.Text, info={'label': 'Private Key', 'description': 'SSH private key.'})
    private_key_passphrase = db.Column(db.String, info={'label': 'Private Key Passphrase', 'description': 'Passphrase to decrypt SSH token. Leave blank if no password is needed'})
    enabled = db.Column(db.Boolean, default=True, info={'label': 'Enable?'})
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'), info={'label': 'Owner', 'description': 'Owner of the Database Credential'})
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))
    uniqueConstrant = db.UniqueConstraint(app_name, owner_id)

    @property
    def botsUsingApp(self):
        from app.modules.bots.models import Bot
        return Bot.query.filter_by(database_credential=self).count()

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user