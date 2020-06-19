import os


class BaseConfig(object):
    VERSION = 'v1.4.2'
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    DD_API_KEY = os.getenv('DD_API_KEY')
    DD_APP_KEY = os.getenv('DD_APP_KEY')
    SENTRY_INTEGRATION_CLIENT_ID = os.getenv('SENTRY_INTEGRATION_CLIENT_ID')
    SENTRY_INTEGRATION_CLIENT_SECRET = os.getenv('SENTRY_INTEGRATION_CLIENT_SECRET')
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    SCHEMA_NAME = os.getenv('SCHEMA_NAME', 'credential_store')
    DB_USER = 'postgres'
    DB_PASSWORD = ''
    DB_NAME = 'postgres'
    DB_HOST = 'localhost'
    DB_PORT = 5432
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    DEBUG = False
    ERROR_404_HELP = False

    SWAGGER_SUPPORTED_SUBMIT_METHODS = ['get', 'put', 'post', 'delete', 'patch']
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True

    AUTHORIZATIONS = {
        'api_token': {'type': 'apiKey', 'in': 'header', 'name': 'X-API-TOKEN'},
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
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_ENABLED = False

class ProductionConfig(BaseConfig):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', f'postgresql://{BaseConfig.DB_USER}:{BaseConfig.DB_PASSWORD}@{BaseConfig.DB_HOST}:{BaseConfig.DB_PORT}/{BaseConfig.DB_NAME}')

class TestingConfig(BaseConfig):
    TESTING = True
    SECURITY_HASHING_SCHEMES = ['plaintext']
    SECURITY_PASSWORD_HASH = 'plaintext'
    SECURITY_DEPRECATED_HASHING_SCHEMES = []
    DB_NAME = 'postgres_test'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', f'postgresql://{BaseConfig.DB_USER}:{BaseConfig.DB_PASSWORD}@{BaseConfig.DB_HOST}:{BaseConfig.DB_PORT}/{DB_NAME}')
