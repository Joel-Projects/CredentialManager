import os
from logging import getLogger

from .logging import Logging


logging = Logging()

from .flask_sqlalchemy import SQLAlchemy, Timestamp, InfoAttrs, StrName, QueryProperty
db = SQLAlchemy()

from sqlalchemy_utils import force_auto_coercion, force_instant_defaults
force_auto_coercion()
force_instant_defaults()

from flask_login import LoginManager
login_manager = LoginManager()

from flask_marshmallow import Marshmallow
marshmallow = Marshmallow()

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()

from flask_debugtoolbar import DebugToolbarExtension
debugToolBar = DebugToolbarExtension()

from flask_moment import Moment
moment = Moment()

from flask_cors import CORS
cross_origin_resource_sharing = CORS()

from .frontend.forms import ModelForm
from .frontend.errors import unauthorizedError, notFoundError
from .frontend.decorators import paginateArgs, requiresAdmin, verifyEditable

from . import api

foreignKeyKwargs = dict(ondelete='SET NULL', onupdate='CASCADE')
log = getLogger(__name__)


def init_app(app):
    '''
    Application extensions initialization.
    '''
    extensions = [cross_origin_resource_sharing, logging, db, login_manager, marshmallow, api, bootstrap, moment]
    if int(os.getenv('FLASK_DEBUG', '0')): # pragma: no cover
        extensions.append(debugToolBar)
    for extension in extensions:
        extension.init_app(app)

    app.register_error_handler(403, unauthorizedError)
    app.register_error_handler(404, notFoundError)
    try:
        with db.get_engine(app=app).connect() as sql: # pragma: no cover
            results = sql.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'credential_store';")
            if not results.fetchone():
                raise Exception('Need to manually create schema')
    except Exception as error: # pragma: no cover
        log.exception(error)
    db.create_all(app=app)