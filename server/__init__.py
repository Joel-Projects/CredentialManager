import sentry_sdk, sys, datadog, logging.config, logging, os, inspect
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_wtf import FlaskForm, CSRFProtect

from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from datadog_logger import DatadogLogHandler
from secrets import *
from flask import Flask, Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension

remote = sys.platform == 'darwin'
debug = os.environ.get('CredentialManagerDebug', None) or remote

dsn = sentryDsn
config = {"version": 1, "formatters": {"default": {"format": "%(asctime)s | %(levelname)-8s | %(message)s", "datefmt": "%m/%d/%Y %I:%M:%S %p"}}, "handlers": {"consoleHandler": {"class": "logging.StreamHandler", "level": ('INFO', 'DEBUG')[sys.platform == 'darwin'], "formatter": "default", "stream": "ext://sys.stdout"}}, "loggers": {'FlairBotMgmt': {"level": "INFO", "handlers": ["consoleHandler"]}}}
sentry_logging = LoggingIntegration(level=logging.INFO)
logging.config.dictConfig(config)

log = logging.getLogger('CredentialManager')
datadog.initialize(api_key=ddApiKey, app_key=ddAppKey)
log.addHandler(DatadogLogHandler(level=logging.WARNING))
if not remote:
    sentry_sdk.init(dsn=dsn, integrations=[sentry_logging, FlaskIntegration()], attach_stacktrace=True)

app = Flask(__name__, static_folder='./static')

if debug:
    from .config import DevelopmentConfig as settings
else:
    from .config import ProductionConfig as settings

app.config.from_object(settings)

if debug:
    DebugToolbarExtension().init_app(app)

app.url_map.strict_slashes = False
app.jinja_env.cache = {}
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.auto_reload = True


db = SQLAlchemy(app)
from . import models
from .models import User, RedditApp, RefreshToken, Sentry, Bot
db.init_app(app)
# db.drop_all()
db.create_all()
db.session.commit()

with db.engine.connect() as sql:
    sql.execute('''
create extension if not exists pgcrypto with schema public;
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

alter function credential_store.gen_state() owner to postgres;
drop trigger if exists refresh_token_state_hashing_trigger on credential_store.reddit_apps;
create trigger refresh_token_state_hashing_trigger
	before insert or update
	of client_id
	on credential_store.reddit_apps
	for each row
	execute procedure credential_store.gen_state();
    ''')

bootstrap = Bootstrap(app)

csrf = CSRFProtect(app)
csrf.init_app(app)

@app.before_request
def check_csrf():
    if not 'key' in request.form:
        csrf.protect()

from .serializers import UserSerializer, BotSerializer, RedditAppSerializer, RefreshTokenSerializer, SentrySerializer, DatabaseSerializer, ApiTokenSerializer
userSerializer = UserSerializer()
botSerializer = BotSerializer()
redditAppSerializer = RedditAppSerializer()
refreshTokenSerializer = RefreshTokenSerializer()
sentrySerializer = SentrySerializer()
databaseSerializer = DatabaseSerializer()
apiTokenSerializer = ApiTokenSerializer()
from .helpers import items
from .decorators import apiAccessible
appApi = Api(app, prefix='/api', decorators=[apiAccessible])
from .api import user, common

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from . import blueprints
isBlueprint = lambda blueprint: (isinstance(blueprint, Blueprint))
blueprints = [blueprint[1] for blueprint in inspect.getmembers(blueprints, isBlueprint)]
for blueprint in blueprints:
    app.register_blueprint(blueprint)

