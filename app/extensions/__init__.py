'''
Extensions setup
================

Extensions provide access to common resources of the application.

Please, put new extension instantiations and initializations here.
'''
from ..secrets import *

from .logging import Logging
logging = Logging()

from flask_cors import CORS
cross_origin_resource_sharing = CORS()

from .flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from sqlalchemy_utils import force_auto_coercion, force_instant_defaults
force_auto_coercion()
force_instant_defaults()

from flask_login import LoginManager
login_manager = LoginManager()

from flask_marshmallow import Marshmallow
marshmallow = Marshmallow()

# from flask_wtf import CSRFProtect
# csrf = CSRFProtect()

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()

from flask_debugtoolbar import DebugToolbarExtension
debugToolBar = DebugToolbarExtension()

from .frontend.forms import ModelForm

from . import api

foreignKeyKwargs = dict(ondelete='SET NULL', onupdate='CASCADE')

def init_app(app):
    '''
    Application extensions initialization.
    '''
    for extension in (
            logging,
            cross_origin_resource_sharing,
            db,
            login_manager,
            marshmallow,
            api,
            # csrf,
            bootstrap,
            debugToolBar
        ):
        extension.init_app(app)

    db.create_all(app=app)