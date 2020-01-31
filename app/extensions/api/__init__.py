'''
API extension
=============
'''

from copy import deepcopy

from .api import Api
from .namespace import Namespace
from .http_exceptions import abort


api_v1 = Api(
    version='1.0',
    title='Credential Manager API',
    description='API for interacting with Credential Manager',
    default=None,
    # default_label='User Management',
    doc='/docs/',
    security=['apiKey', 'basic']
)

def init_app(app, **kwargs):
    '''
    API extension initialization point.
    '''
    # Prevent config variable modification with runtime changes
    api_v1.authorizations = deepcopy(app.config['AUTHORIZATIONS'])