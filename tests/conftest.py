import pytest
from flask_login import current_user, login_user, logout_user

from app import create_app
from app.modules.users import models
from tests import utils


@pytest.fixture()
def flask_app():
    app = create_app(flask_config_name="testing")
    from app.extensions import db

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture()
def db(flask_app):
    from app.extensions import db as db_instance

    yield db_instance


@pytest.fixture()
def temp_db_instance_helper(db):
    def temp_db_instance_manager(instance):
        with db.session.begin():
            db.session.add(instance)

        yield instance

    return temp_db_instance_manager


@pytest.fixture()
def flask_app_client(flask_app):
    flask_app.test_client_class = utils.AutoAuthFlaskClient
    flask_app.response_class = utils.JSONResponse
    context = flask_app.app_context()
    context.push()
    yield flask_app.test_client()
    context.pop()


@pytest.yield_fixture(scope="session")
def patch_user_password_scheme():
    """
    By default, the application uses ``bcrypt`` to store passwords securely.
    However, ``bcrypt`` is a slow hashing algorithm (by design), so it is
    better to downgrade it to ``plaintext`` while testing, since it will save
    us quite some time.
    """
    # NOTE: It seems a hacky way, but monkeypatching is a hack anyway.
    password_field_context = models.User.password.property.columns[0].type.context
    # NOTE: This is used here to forcefully resolve the LazyCryptContext
    _ = password_field_context.context_kwds
    password_field_context._config._init_scheme_list(("plaintext",))
    password_field_context._config._init_records()
    password_field_context._config._init_default_schemes()
    yield
    password_field_context._config._init_scheme_list(("bcrypt",))
    password_field_context._config._init_records()
    password_field_context._config._init_default_schemes()


@pytest.fixture()
def regular_user(temp_db_instance_helper, patch_user_password_scheme):
    for item in temp_db_instance_helper(utils.generate_user_instance(username="regular_user")):
        yield item


@pytest.fixture()
def admin_user(temp_db_instance_helper, patch_user_password_scheme):
    for item in temp_db_instance_helper(utils.generate_user_instance(username="admin_user", is_admin=True)):
        yield item


@pytest.fixture()
def internal_user(temp_db_instance_helper, patch_user_password_scheme):
    for item in temp_db_instance_helper(
        utils.generate_user_instance(
            username="internal_user",
            is_regular_user=False,
            is_admin=False,
            is_internal=True,
        )
    ):
        yield item


@pytest.fixture()
def user_instance(patch_user_password_scheme, temp_db_instance_helper):
    for _user_instance in temp_db_instance_helper(
        utils.generate_user_instance(username="username", password="password")
    ):
        user_id = _user_instance.id
        _user_instance.get_id = lambda: user_id
        return _user_instance


@pytest.fixture()
def regular_user_instance(flask_app, user_instance):
    with flask_app.test_request_context("/"):
        login_user(user_instance)
        yield current_user
        logout_user()


@pytest.fixture()
def admin_user_instance(flask_app, user_instance):
    with flask_app.test_request_context("/"):
        login_user(user_instance)
        current_user.is_admin = True
        yield current_user
        logout_user()


@pytest.fixture()
def internal_user_instance(flask_app, user_instance):
    with flask_app.test_request_context("/"):
        login_user(user_instance)
        current_user.is_internal = True
        yield current_user
        logout_user()


@pytest.fixture()
def anonymous_user_instance(flask_app):
    with flask_app.test_request_context("/"):
        yield current_user
