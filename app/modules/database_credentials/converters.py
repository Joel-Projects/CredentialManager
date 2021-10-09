from werkzeug.routing import BaseConverter

from app.extensions.api import abort

from .models import DatabaseCredential


class DatabaseCredentialConverter(BaseConverter):
    def to_python(self, value):
        database_credential = DatabaseCredential.query.filter(DatabaseCredential.id == value).first()
        if database_credential:
            return database_credential
        else:
            abort(404)
