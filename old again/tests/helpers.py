import flask
from flask.testing import FlaskClient as BaseFlaskClient
from flask_wtf.csrf import generate_csrf

class RequestShim(object):
    def __init__(self, client):
        self.client = client
        self.vary = set({})

    def set_cookie(self, key, value='', *args, **kwargs):
        "Set the cookie on the Flask test client."
        server_name = flask.current_app.config["SERVER_NAME"] or "localhost"
        kwargs.pop('samesite')
        return self.client.set_cookie(server_name, key=key, value=value, *args, **kwargs)

    def delete_cookie(self, key, *args, **kwargs):
        "Delete the cookie on the Flask test client."
        server_name = flask.current_app.config["SERVER_NAME"] or "localhost"
        kwargs.pop('samesite')
        return self.client.delete_cookie(server_name, key=key, *args, **kwargs)

class FlaskClient(BaseFlaskClient):
    @property
    def csrf_token(self):
        request = RequestShim(self)
        environ_overrides = {}
        self.cookie_jar.inject_wsgi(environ_overrides)
        with flask.current_app.test_request_context("/login", environ_overrides=environ_overrides):
            csrf_token = generate_csrf()
            flask.current_app.session_interface.save_session(self.application, flask.session, request)
            return csrf_token

    def post(self, *args, **kw):
        kw["method"] = "POST"
        if not 'key' in kw['data']:
            kw['data']['csrf_token'] = self.csrf_token
        return self.open(*args, **kw)

    def patch(self, *args, **kw):
        kw["method"] = "PATCH"
        if not 'key' in kw['data']:
            kw['data']['csrf_token'] = self.csrf_token
        return self.open(*args, **kw)

    def put(self, *args, **kw):
        kw["method"] = "PUT"
        if not 'key' in kw['data']:
            kw['data']['csrf_token'] = self.csrf_token
        return self.open(*args, **kw)

    def delete(self, *args, **kw):
        kw["method"] = "DELETE"
        if not 'key' in kw['data']:
            kw['data']['csrf_token'] = self.csrf_token
        return self.open(*args, **kw)
