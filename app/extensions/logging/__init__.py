import logging, datadog, sentry_sdk, sys
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from datadog_logger import DatadogLogHandler


class Logging(object):

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        # We don't need the default Flask's loggers when using our invoke tasks
        # since we set up beautiful colorful loggers globally.
        for handler in list(app.logger.handlers):
            app.logger.removeHandler(handler)
        app.logger.propagate = True

        if app.debug:
            app.logger.setLevel(logging.DEBUG)

        remote = sys.platform == 'darwin'
        dsn = app.config['SENTRY_DSN']
        ddApiKey = app.config['DD_API_KEY']
        ddAppKey = app.config['DD_APP_KEY']
        sentry_logging = LoggingIntegration(level=logging.INFO)
        if ddApiKey and ddAppKey:
            datadog.initialize(api_key=ddApiKey, app_key=ddAppKey)
            app.logger.addHandler(DatadogLogHandler(level=logging.WARNING))
        if remote and dsn:
            sentry_sdk.init(dsn=dsn, integrations=[sentry_logging, FlaskIntegration()], attach_stacktrace=True)

        logging.basicConfig()
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        # logging.getLogger('app').setLevel(logging.DEBUG)

        try:
            import colorlog
        except ImportError:
            pass
        else:
            formatter = colorlog.ColoredFormatter('%(asctime)s [%(log_color)s%(levelname)s%(reset)s] [%(cyan)s%(name)s%(reset)s] %(message_log_color)s%(message)s', reset=True, log_colors={'DEBUG': 'bold_cyan', 'INFO': 'bold_green', 'WARNING': 'bold_yellow', 'ERROR': 'bold_red', 'CRITICAL': 'bold_red,bg_white', }, secondary_log_colors={'message': {'DEBUG': 'white', 'INFO': 'bold_white', 'WARNING': 'bold_yellow', 'ERROR': 'bold_red', 'CRITICAL': 'bold_red'}}, style='%', datefmt='%m/%d/%Y %I:%M:%S %p %Z')

            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    break
            else:
                handler = logging.StreamHandler()
                logger.addHandler(handler)
            handler.setFormatter(formatter)