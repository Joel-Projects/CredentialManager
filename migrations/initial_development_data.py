# pylint: disable=missing-docstring
"""
This file contains initialization data for development usage only.

You can execute this code via ``invoke app.db.init_development_data``
"""
from app.extensions import db, api

from app.modules.users.models import User
from app.modules.api_tokens.models import ApiToken


def init_users():
    with db.session.begin():
        root_user = User(
            username='root',
            password='q',
            is_active=True,
            is_regular_user=True,
            is_admin=True
        )
        db.session.add(root_user)
        docs_user = User(
            username='documentation',
            password='w',
            is_active=False
        )
        db.session.add(docs_user)
        regular_user = User(
            username='user',
            password='w',
            is_active=True,
            is_regular_user=True
        )
        db.session.add(regular_user)
        internal_user = User(
            username='internal',
            password='q',
            is_active=True,
            is_internal=True
        )
        db.session.add(internal_user)
    return root_user, docs_user, regular_user

def init_auth(root_user, docs_user, regular_user ):
    with db.session.begin():
        apiToken = ApiToken(name='test', token='secret', owner_id=docs_user.id,)
        db.session.add(apiToken)
        apiToken2 = ApiToken(name='test', token='secret', owner_id=root_user.id,)
        db.session.add(apiToken2)
        apiToken3 = ApiToken(name='test', token='secret', owner_id=regular_user.id,)
        db.session.add(apiToken3)
    return apiToken

def init():

    assert User.query.count() == 0,  "Database is not empty. You should not re-apply fixtures! Aborted."

    root_user, docs_user, regular_user = init_users()
    init_auth(root_user, docs_user, regular_user)
