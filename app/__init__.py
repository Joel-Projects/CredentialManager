import os
import sys

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

config_name_mapper = {
    "development": "config.DevelopmentConfig",
    "testing": "config.TestingConfig",
    "production": "config.ProductionConfig",
    "local": "local_config.LocalConfig",
}


def create_app(flask_config_name=None, **kwargs):

    app = Flask(__name__, **kwargs)

    env_flask_config_name = os.getenv("FLASK_CONFIG")
    if not env_flask_config_name and flask_config_name is None:
        flask_config_name = "local"
    elif flask_config_name is None:
        flask_config_name = env_flask_config_name
    else:
        if env_flask_config_name:
            assert (
                env_flask_config_name == flask_config_name
            ), f"FLASK_CONFIG environment variable ({env_flask_config_name!r}) and flask_config_name argument ({flask_config_name!r}) are both set and are not the same."
    try:
        app.config.from_object(config_name_mapper[flask_config_name])
    except ImportError:
        if flask_config_name == "local":
            app.logger.error(
                'You have to have `local_config.py` or `local_config/__init__.py` in order to use the default "local" Flask Config. Alternatively, you may set `FLASK_CONFIG` environment variable to one of the following options: development, production, testing.'
            )
            sys.exit(1)
        raise

    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.url_map.strict_slashes = False
    app.jinja_env.cache = {}
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.auto_reload = True
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")
    from . import extensions

    extensions.init_app(app)

    from . import modules

    modules.init_app(app)
    db = extensions.db
    db.create_all(app=app)
    app.logger.info("app initialized")
    return app
