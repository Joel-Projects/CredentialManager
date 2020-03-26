import re

from flask_login import current_user
from wtforms.fields import StringField
from wtforms.validators import HostnameValidation, Regexp
from wtforms_alchemy import InputRequired, Length, Unique

from app.extensions import ModelForm
from .models import SentryToken
from ...extensions.frontend.forms import AppSelectField, owners


class SentryHostnameValidation(HostnameValidation):
    hostname_part = re.compile(r'^(xn-|[a-z0-9@]+)(-[a-z0-9@]+)*$', re.IGNORECASE)

class SentryTokenValidator(Regexp):
    def __init__(self, require_tld=True, message=None):
        regex = r'^[a-z]+://(?P<host>[^/:]+)(?P<port>:[0-9]+)?(?P<path>\/.*)?$'
        super(SentryTokenValidator, self).__init__(regex, re.IGNORECASE, message)
        self.validate_hostname = SentryHostnameValidation(require_tld=require_tld, allow_ip=True,)

class SentryTokenForm(ModelForm):
    class Meta:
        model = SentryToken
        only = ['dsn', 'enabled']
        field_args = {'enabled': {'default': True}}

    app_name = StringField('Name', validators=[InputRequired(), Unique([SentryToken.owner, SentryToken.app_name]), Length(3)])
    dsn = StringField('DSN', validators=[InputRequired(), SentryTokenValidator(message='Invalid Sentry Token')])
    owner = AppSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user)