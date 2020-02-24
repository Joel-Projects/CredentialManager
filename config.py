import os

class BaseConfig(object):
    SECRET_KEY = 'this-really-needs-to-be-changed'

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    # POSTGRESQL
    DB_USER = 'postgres'
    DB_PASSWORD = ''
    DB_NAME = 'postgres'
    DB_HOST = 'localhost'
    DB_PORT = 5432
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    DEBUG = False
    ERROR_404_HELP = False

    SWAGGER_SUPPORTED_SUBMIT_METHODS = ["get", "put", "post", "delete", "patch"]
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True

    AUTHORIZATIONS = {
        'apiKey': {'type': 'apiKey', 'in': 'header', 'name': 'X-API-KEY'},
        'basic': {'type': 'basic'}
    }

    ENABLED_MODULES = (
        'auth',
        'frontend',
        'users',
        'api_tokens',
        'database_credentials',
        'reddit_apps',
        'sentry_tokens',
        'bots',
        'refresh_tokens',
        'user_verifications',
        'api',
    )

    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

    SWAGGER_UI_JSONEDITOR = True

    # TODO: consider if these are relevant for this project
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_ENABLED = False

class ProductionConfig(BaseConfig):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

class TestingConfig(BaseConfig):
    TESTING = True

    DB_NAME = 'postgres_test'
    SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig.DB_USER}:{BaseConfig.DB_PASSWORD}@{BaseConfig.DB_HOST}:{BaseConfig.DB_PORT}/{DB_NAME}'
