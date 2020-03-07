from app.extensions.api import abort
from app.modules.api_tokens.models import ApiToken
from werkzeug.routing import BaseConverter

class ApiTokenConverter(BaseConverter):

    def to_python(self, value):
        return ApiToken.query.filter(ApiToken.id == value).first_or_404()