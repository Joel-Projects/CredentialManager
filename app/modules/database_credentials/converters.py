from app.extensions.api import abort
from .models import DatabaseCredential
from werkzeug.routing import BaseConverter

class DatabaseCredentialConverter(BaseConverter):

    def to_python(self, value):
        DatabaseCredential = DatabaseCredential.query.filter(DatabaseCredential.id == value).first()
        if DatabaseCredential:
            return DatabaseCredential
        else:
            abort(404)