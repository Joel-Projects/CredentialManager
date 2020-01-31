"""
Testing utils
-------------
"""

from contextlib import contextmanager
from datetime import datetime, timedelta
import json, flask

from flask import Response
from flask.testing import FlaskClient
from werkzeug.utils import cached_property
from flask_login import login_user, current_user, logout_user
from base64 import b64encode
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


class AutoAuthFlaskClient(FlaskClient):
    """
    A helper FlaskClient class with a useful for testing ``login`` context
    manager.
    """

    def __init__(self, *args, **kwargs):
        super(AutoAuthFlaskClient, self).__init__(*args, **kwargs)
        self._user = None

    @contextmanager
    def login(self, user):
        # @self.application.login_manager.request_loader
        # def load_user_from_request(request):
        #     return user

        with self.application.test_request_context():
            if user:
                self.post('/login', data={'username': user.username, 'password': user.password_secret}, follow_redirects=True)
            self._user = user
            yield self
            self.post('/logout', follow_redirects=True)
            self._user = None

    def open(self, *args, **kwargs):
        if self._user is not None:

            extra_headers = {'Authorization': f'Basic {b64encode(f"{self._user.username}:password".encode()).decode("ascii")}'}
            if kwargs.get('headers'):
                if not 'Authorization' in kwargs.get('headers') and not 'X-API-KEY' in kwargs.get('headers'):
                    kwargs['headers'] += extra_headers
            else:
                kwargs['headers'] = extra_headers

        return super(AutoAuthFlaskClient, self).open(*args, **kwargs)

class JSONResponse(Response):
  
    """
    A Response class with extra useful helpers, i.e. ``.json`` property.
    """

    @cached_property
    def json(self):
        return json.loads(self.get_data(as_text=True))


def generate_user_instance(user_id=None,username="username", password=None, default_redirect_uri='http://localhost:8080/callback', created=None, updated=None, is_active=True, is_regular_user=True, is_admin=False, is_internal=False):
    """
    Returns:
        user_instance (User) - an not committed to DB instance of a User model.
    """
  
    from app.modules.users.models import User
    if password is None:
        password = f'{username}_password'
    user_instance = User(
        id=user_id,
        username=username,
        password=password,
        default_redirect_uri=default_redirect_uri,
        created=created or datetime.now(),
        updated=updated or datetime.now(),
        is_active=is_active,
        is_regular_user=is_regular_user,
        is_admin=is_admin,
        is_internal=is_internal
    )
    user_instance.password_secret = password
    return user_instance