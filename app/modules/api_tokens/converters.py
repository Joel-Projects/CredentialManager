from werkzeug.routing import BaseConverter

from app.modules.api_tokens.models import ApiToken


class ApiTokenConverter(BaseConverter):
    def to_python(self, value):
        return ApiToken.query.filter(ApiToken.id == value).first_or_404()
