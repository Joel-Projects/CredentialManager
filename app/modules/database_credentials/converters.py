from werkzeug.routing import BaseConverter

from app.extensions.api import abort
from .models import DatabaseCredential


class DatabaseCredentialConverter(BaseConverter):

    def to_python(self, value):
        databaseCredential = DatabaseCredential.query.filter(DatabaseCredential.id == value).first()
        if databaseCredential:
            return databaseCredential
        else:
            abort(404)