import re

from flask_login import current_user
from wtforms.fields import StringField
from wtforms.validators import HostnameValidation, Regexp, StopValidation
from wtforms_alchemy import InputRequired, Length, Unique
from wtforms import SelectField

from app.extensions import ModelForm
from .models import SentryToken
from ...extensions.frontend.forms import HiddenFieldWithToggle, ModelSelectField, owners


class SentryHostnameValidation(HostnameValidation):
    hostname_part = re.compile(r'^(xn-|[a-z0-9@]+)(-[a-z0-9@]+)*$', re.IGNORECASE)

class SentryTokenValidator(Regexp):
    def __init__(self, require_tld=True, message=None, createSentryAppField=None):
        self.createSentryAppField = createSentryAppField
        regex = r'^[a-z]+://(?P<host>[^/:]+)(?P<port>:[0-9]+)?(?P<path>\/.*)?$'
        super(SentryTokenValidator, self).__init__(regex, re.IGNORECASE, message)
        self.validate_hostname = SentryHostnameValidation(require_tld=require_tld, allow_ip=True,)

    def __call__(self, *args, **kwargs):
        if not self.createSentryAppField:
            super(SentryTokenValidator, self).__call__(*args, **kwargs)
        else:
            return True

class SentryDSNValidator:
    def __init__(self, createSentryAppField, message=None):
        self.createSentryAppField = createSentryAppField
        self.message = message

    def __call__(self, form, field):
        if not form.create_sentry_app.data:
            if self.message is None:
                message = field.gettext('This field is required.')
            else:
                message = self.message

            field.errors[:] = []
            raise StopValidation(message)

class EditSentryTokenForm(ModelForm):
    class Meta:
        model = SentryToken
        only = ['dsn', 'enabled']
        field_args = {'enabled': {'default': True}}

    app_name = StringField('Name', validators=[InputRequired(), Unique([SentryToken.owner, SentryToken.app_name]), Length(3)])
    dsn = StringField('DSN', validators=[InputRequired(), SentryTokenValidator(message='Invalid Sentry Token')])
    owner = ModelSelectField(query_factory=owners, queryKwargs={'current_user': current_user}, default=current_user)

class CreateSentryTokenForm(EditSentryTokenForm):
    create_sentry_app = HiddenFieldWithToggle('Create app on Sentry?', default=False, render_kw={'value': ''})
    dsn = StringField('DSN', validators=[SentryDSNValidator(create_sentry_app), SentryTokenValidator(message='Invalid Sentry Token', createSentryAppField=create_sentry_app)])
    sentry_organization = SelectField('Sentry Organization', validate_choice=False)
    sentry_team = SelectField('Sentry Team', validate_choice=False)