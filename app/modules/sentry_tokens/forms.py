import re

from flask_login import current_user
from wtforms.fields import SubmitField, FormField, StringField
from wtforms.validators import URL, Regexp, HostnameValidation

from app.extensions import ModelForm
from wtforms_alchemy import Length, Unique, InputRequired
from .models import SentryToken
from ...extensions.frontend.forms import AppSelectField, owners

class SentryHostnameValidation(HostnameValidation):
    hostname_part = re.compile(r'^(xn-|[a-z0-9@]+)(-[a-z0-9@]+)*$', re.IGNORECASE)

class SentryTokenValidator(Regexp):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, require_tld=True, message=None):
        regex = r'^[a-z]+://(?P<host>[^/:]+)(?P<port>:[0-9]+)?(?P<path>\/.*)?$'
        super(SentryTokenValidator, self).__init__(regex, re.IGNORECASE, message)
        self.validate_hostname = SentryHostnameValidation(require_tld=require_tld,allow_ip=True,)

class SentryTokenForm(ModelForm):
    class Meta:
        model = SentryToken
        only = ['dsn', 'enabled']
        field_args = {'enabled': {'default': True}}
    app_name = StringField('Name', validators=[InputRequired(), Unique([SentryToken.owner, SentryToken.app_name]), Length(3)])
    dsn = StringField('DSN', validators=[InputRequired(), SentryTokenValidator()])
    owner = AppSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user)