import logging
import sys

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


class Logging(object):
    def __init__(self, app=None):
        if app:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        for handler in list(app.logger.handlers):  # pragma: no cover
            app.logger.removeHandler(handler)
        app.logger.propagate = True
        if app.debug:
            app.logger.setLevel(logging.DEBUG)

        dsn = app.config["SENTRY_DSN"]
        sentry_logging = LoggingIntegration(level=logging.INFO)
        if not app.debug and dsn:  # pragma: no cover
            sentry_sdk.init(
                dsn=dsn,
                integrations=[sentry_logging, FlaskIntegration()],
                attach_stacktrace=True,
            )

        try:
            import colorlog
        except ImportError:  # pragma: no cover
            pass
        else:
            formatter = colorlog.ColoredFormatter(
                "%(asctime)s [%(log_color)s%(levelname)s%(reset)s] [%(cyan)s%(name)s%(reset)s] %(message_log_color)s%(message)s",
                reset=True,
                log_colors={
                    "DEBUG": "bold_cyan",
                    "INFO": "bold_green",
                    "WARNING": "bold_yellow",
                    "ERROR": "bold_red",
                    "CRITICAL": "bold_red,bg_white",
                },
                secondary_log_colors={
                    "message": {
                        "DEBUG": "white",
                        "INFO": "bold_white",
                        "WARNING": "bold_yellow",
                        "ERROR": "bold_red",
                        "CRITICAL": "bold_red",
                    }
                },
                style="%",
                datefmt="%m/%d/%Y %I:%M:%S %p %Z",
            )
            gunicorn_error_logger = logging.getLogger("gunicorn.error")
            gunicorn_access_logger = logging.getLogger("gunicorn.access")
            flask_caching_logger = logging.getLogger("flask_caching")
            flask_caching_logger.setLevel(logging.DEBUG)
            app.logger.handlers = gunicorn_error_logger.handlers
            for handler in app.logger.handlers + gunicorn_access_logger.handlers:
                handler.setFormatter(formatter)
                handler.setLevel(gunicorn_error_logger.level)
