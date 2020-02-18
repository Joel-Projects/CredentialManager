'''
Extensions setup
================

Extensions provide access to common resources of the application.

Please, put new extension instantiations and initializations here.
'''
import os
from .logging import Logging

logging = Logging()

from .flask_sqlalchemy import SQLAlchemy, Timestamp, InfoAttrs, StrName
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

from .frontend.forms import ModelForm
from .frontend.errors import unauthorizedError, notFoundError
from .frontend.decorators import paginateArgs, requiresAdmin, verifyEditable

from . import api

foreignKeyKwargs = dict(ondelete='SET NULL', onupdate='CASCADE')

def init_app(app):
    '''
    Application extensions initialization.
    '''
    extensions = [logging, db, login_manager, marshmallow, api, bootstrap]
    if int(os.getenv('FLASK_DEBUG', '0')):
        extensions.append(debugToolBar)
    for extension in extensions:
        extension.init_app(app)

    app.register_error_handler(403, unauthorizedError)
    app.register_error_handler(404, notFoundError)
    db.create_all(app=app)
    from app.modules.users.models import User
    with app.app_context():
        with db.session.begin():
            if User.query.count() == 0:
                internalUser = User(username='internal', password='q', is_active=True, is_regular_user=True, is_internal=True)
                db.session.add(internalUser)
                internalUser.created_by = internalUser.updated_by = 1
                rootUser = User(username='root', password='q', is_active=True, is_regular_user=True, is_admin=True, created_by=1, updated_by=1)
                db.session.add(rootUser)
    try:
        with db.get_engine(app=app).connect() as sql:
            sql.execute('''
    create or replace function credential_store.gen_state() returns trigger
        language plpgsql
    as $$
    BEGIN
        IF tg_op = 'INSERT' OR tg_op = 'UPDATE' THEN
            NEW.state = encode(public.digest(NEW.client_id, 'sha256'), 'hex');
            RETURN NEW;
        END IF;
    END;
    $$;
    
    alter function credential_store.gen_state() owner to credential_manager;
    drop trigger if exists refresh_token_state_hashing_trigger on credential_store.reddit_apps;
    create trigger refresh_token_state_hashing_trigger
        before insert or update
        of client_id
        on credential_store.reddit_apps
        for each row
        execute procedure credential_store.gen_state();
        ''')
    except Exception as error:
        print(error)