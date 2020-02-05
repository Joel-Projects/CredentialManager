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

def init_auth(docs_user):
    # TODO: OpenAPI documentation has to have OAuth2 Implicit Flow instead of Resource Owner Password Credentials Flow
    with db.session.begin():
        apiToken = ApiToken(name='test', token='secret', owner_id=docs_user.id,)
        db.session.add(apiToken)
    return apiToken

def init():
    # Automatically update `default_scopes` for `documentation` OAuth2 Client,
    # as it is nice to have an ability to evaluate all available API calls.
    # with db.session.begin():
    #     OAuth2Client.query.filter(OAuth2Client.client_id == 'documentation').update({
    #         OAuth2Client.default_scopes: api.api_v1.authorizations['oauth2_password']['scopes'],
    #     })

    assert User.query.count() == 0,  "Database is not empty. You should not re-apply fixtures! Aborted."

    root_user, docs_user, regular_user = init_users()
    init_auth(docs_user)
