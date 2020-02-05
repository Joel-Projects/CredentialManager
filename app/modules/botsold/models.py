from app.extensions import db, foreignKeyKwargs, Timestamp

class Bot(db.Model, Timestamp):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'bots'
    __table_args__ = {'schema': 'credential_store'}
    id = db.Column(db.Integer, primary_key=True)
    bot_name = db.Column(db.String(length=50), nullable=False)
    # reddit_id = db.Column(db.Integer, db.ForeignKey('credential_store.reddit_apps.id', **foreignKeyKwargs))
    reddit_id = db.Column(db.Integer, db.ForeignKey('reddit_apps.id', **foreignKeyKwargs))
    reddit = db.relationship('RedditApp', backref=db.backref(__tablename__, lazy='dynamic'))
    # sentry_id = db.Column(db.Integer, db.ForeignKey('credential_store.sentry_tokens.id', **foreignKeyKwargs))
    sentry_id = db.Column(db.Integer, db.ForeignKey('sentry_tokens.id', **foreignKeyKwargs))
    sentry = db.relationship('Sentry', backref=db.backref(__tablename__, lazy='dynamic'))
    # database_id = db.Column(db.Integer, db.ForeignKey('credential_store.database_credentials.id', **foreignKeyKwargs))
    database_id = db.Column(db.Integer, db.ForeignKey('database_credentials.id', **foreignKeyKwargs))
    database = db.relationship('Database', backref=db.backref(__tablename__, lazy='dynamic'))
    enabled = db.Column(db.Boolean, default=True)
    # owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'))
    owner_id = db.Column(db.Integer, db.ForeignKey('credential_store.users.id', ondelete='CASCADE', onupdate='CASCADE'))
    owner = db.relationship('User', backref=db.backref(__tablename__, lazy='dynamic'))

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, bot_name='{self.bot_name}')>"

    @db.validates('bot_name')
    def validate_bot_name(self, key, bot_name):
        if len(bot_name) < 3:
            raise ValueError('Bot name has to be at least 3 characters long.')
        return bot_name
