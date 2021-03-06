import logging

from flask import jsonify
from flask_restplus import Api as OriginalApi
from flask_restplus._http import HTTPStatus
from werkzeug import cached_property

from .namespace import Namespace
from .swagger import Swagger

log = logging.getLogger(__name__)


class Api(OriginalApi):
    @cached_property
    def __schema__(self):
        # The only purpose of this method is to pass custom Swagger class
        if not self._schema:
            self._schema = Swagger(self).as_dict()
        return self._schema

    def init_app(self, app, **kwargs):
        # This solves the issue of late resources registration:
        # https://github.com/frol/flask-restplus-server-example/issues/110
        # https://github.com/noirbizarre/flask-restplus/pull/483
        self.app = app

        super(Api, self).init_app(app, **kwargs)
        app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY.value)(handle_validation_error)

    def namespace(self, *args, **kwargs):  # pragma: no cover
        # The only purpose of this method is to pass a custom Namespace class
        kwargs["ordered"] = kwargs.get("ordered", self.ordered)
        _namespace = Namespace(*args, **kwargs)
        self.add_namespace(_namespace)
        return _namespace


# Return validation errors as JSON
def handle_validation_error(err):  # pragma: no cover
    exc = err.data["exc"]
    return (
        jsonify({"status": HTTPStatus.UNPROCESSABLE_ENTITY.value, "message": exc.messages}),
        HTTPStatus.UNPROCESSABLE_ENTITY.value,
    )
