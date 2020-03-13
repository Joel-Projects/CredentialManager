import operator

import sqlalchemy
from datetime import datetime
from sqlalchemy import Column, DateTime
from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy, _QueryProperty


class AlembicDatabaseMigrationConfig(object):
    '''
    Helper config holder that provides missing functions of Flask-Alembic
    package since we use custom invoke tasks instead.
    '''

    def __init__(self, database, directory='migrations', **kwargs):
        self.db = database
        self.directory = directory
        self.configure_args = kwargs

class SQLAlchemy(BaseSQLAlchemy):
    def __init__(self, *args, **kwargs):
        if 'session_options' not in kwargs:
            kwargs['session_options'] = {}
        kwargs['session_options']['autocommit'] = True
        super(SQLAlchemy, self).__init__(*args, **kwargs)

    def init_app(self, app):
        super(SQLAlchemy, self).init_app(app)

        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        assert database_uri, 'SQLALCHEMY_DATABASE_URI must be configured!'

        app.extensions['migrate'] = AlembicDatabaseMigrationConfig(self, compare_type=True)

class Timestamp(object):
    created = Column(DateTime(True), default=datetime.astimezone(datetime.utcnow()), nullable=False)
    updated = Column(DateTime(True), default=datetime.astimezone(datetime.utcnow()), nullable=False)

# noinspection PyUnresolvedReferences
@sqlalchemy.event.listens_for(Timestamp, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated = datetime.astimezone(datetime.utcnow())

class InfoAttrs(object):

    def getInfoAttr(self, path):
        try:
            attr = operator.attrgetter(path)(self)
            if callable(attr):
                attr = attr()
        except AttributeError:
            attr = None
        return attr

class StrName(object):

    def __str__(self):
        return getattr(self, self._nameAttr)

class QueryProperty(object):
    query = _QueryProperty(super(SQLAlchemy))