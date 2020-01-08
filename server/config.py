import os
from secrets import secretKey, dbUri

localPostgres = 'postgresql://postgres:@localhost/postgres'

class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', secretKey)
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = dbUri


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = localPostgres


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    # CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = localPostgres + '_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', secretKey)

    DEBUG = False
