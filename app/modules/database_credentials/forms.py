from flask_login import current_user
from wtforms.fields import StringField, BooleanField
from wtforms.validators import Optional
from wtforms.widgets import HTMLString

from app.extensions import ModelForm
from wtforms_alchemy import QuerySelectField, InputRequired
from .models import DatabaseCredential
from ..users.models import User
from ...extensions.frontend.forms import HiddenFieldWithToggle

def owners():
    return User.query

class DatabaseCredentialForm(ModelForm):
    class Meta:
        model = DatabaseCredential
        only = ['app_name', 'database_flavor', 'database_host', 'database_port', 'database_username', 'database_password', 'database', 'use_ssh', 'ssh_host', 'ssh_port', 'ssh_username', 'ssh_password', 'use_ssh_key', 'private_key', 'private_key_passphrase', 'enabled']
        fields = [['app_name', 'database_flavor'], ['database_host', 'database_port'], ['database_username', 'database_password'], 'database', 'use_ssh', ['ssh_host', 'ssh_port'], ['ssh_username', 'ssh_password'], 'use_ssh_key', 'private_key', 'private_key_passphrase', 'enabled']
    if current_user:
        databaseFlavorDefault = current_user.getDefault('user_agent')
        databaseHostDefault = current_user.getDefault('user_agent')
        sshHostDefault = current_user.getDefault('redirect_uri')
        sshUserDefault = current_user.getDefault('redirect_uri')
    else:
        databaseFlavorDefault = DatabaseCredential.database_flavor.default.arg
        databaseHostDefault = DatabaseCredential.database_host.default.arg
        sshHostDefault = ''
        sshUserDefault = ''
    database_flavor = StringField('Database Flavor', validators=[InputRequired()], default=databaseFlavorDefault, description=DatabaseCredential.database_flavor.info['description'])
    database_host = StringField('Database Host', validators=[InputRequired()], default=databaseHostDefault, description=DatabaseCredential.database_host.info['description'])
    ssh_host = StringField('SSH Host', validators=[Optional()], default=sshHostDefault, description=DatabaseCredential.ssh_host.info['description'])
    ssh_username = StringField('SSH Username', validators=[Optional()], default=sshUserDefault, description=DatabaseCredential.ssh_username.info['description'])

    use_ssh = HiddenFieldWithToggle('Use SSH?', default=False, render_kw={'value': ''})
    use_ssh_key = HiddenFieldWithToggle('Use SSH key?', default=False, render_kw={'value': ''})

    owner = QuerySelectField(query_factory=owners, default=current_user, description=DatabaseCredential.owner_id.info['description'])

