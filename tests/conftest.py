import pytest

from tests import utils

from app import create_app
from app.modules.users import models


@pytest.yield_fixture()
def flask_app():
    app = create_app(flask_config_name='testing')
    from app.extensions import db

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.yield_fixture()
def db(flask_app):
    from app.extensions import db as db_instance
    yield db_instance

@pytest.fixture()
def temp_db_instance_helper(db):
    def temp_db_instance_manager(instance):
        with db.session.begin():
            db.session.add(instance)

        yield instance

        mapper = instance.__class__.__mapper__
        assert len(mapper.primary_key) >= 1
        instance.__class__.query.filter(mapper.primary_key[0] == mapper.primary_key_from_instance(instance)[0]).delete()

    return temp_db_instance_manager

@pytest.fixture()
def flask_app_client(flask_app):
    flask_app.test_client_class = utils.AutoAuthFlaskClient
    flask_app.response_class = utils.JSONResponse
    context = flask_app.app_context()
    context.push()
    yield flask_app.test_client()
    context.pop()

@pytest.yield_fixture()
def patch_User_password_scheme():
    '''
    By default, the application uses ``bcrypt`` to store passwords securely.
    However, ``bcrypt`` is a slow hashing algorithm (by design), so it is
    better to downgrade it to ``plaintext`` while testing, since it will save
    us quite some time.
    '''
    # NOTE: It seems a hacky way, but monkeypatching is a hack anyway.
    password_field_context = models.User.password.property.columns[0].type.context
    # NOTE: This is used here to forcefully resolve the LazyCryptContext
    password_field_context.context_kwds
    password_field_context._config._init_scheme_list(('plaintext',))
    password_field_context._config._init_records()
    password_field_context._config._init_default_schemes()
    yield
    password_field_context._config._init_scheme_list(('bcrypt',))
    password_field_context._config._init_records()
    password_field_context._config._init_default_schemes()

@pytest.yield_fixture()
def regular_user(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='regular_user')):
        yield _

@pytest.yield_fixture()
def regular_user2(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='regular_user2')):
        yield _

@pytest.yield_fixture()
def readonly_user(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='readonly_user', is_regular_user=False)):
        yield _

@pytest.yield_fixture()
def deactivated_regular_user(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='deactivated_regular_user', is_active=False)):
        yield _

@pytest.yield_fixture()
def deactivated_regular_user2(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='deactivated_regular_user2', is_active=False)):
        yield _

@pytest.yield_fixture()
def deactivated_admin_user(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='deactivated_admin_user', is_active=False, is_admin=True)):
        yield _

@pytest.yield_fixture()
def deactivated_admin_user2(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='deactivated_admin_user2', is_active=False, is_admin=True)):
        yield _

@pytest.yield_fixture()
def admin_user(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='admin_user', is_admin=True)):
        yield _

@pytest.yield_fixture()
def admin_user2(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='admin_user2', is_admin=True)):
        yield _

@pytest.yield_fixture()
def internal_user(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='internal_user', is_regular_user=False, is_admin=False, is_active=True, is_internal=True)):
        yield _

@pytest.yield_fixture()
def internal_user2(temp_db_instance_helper, patch_User_password_scheme):
    for _ in temp_db_instance_helper(utils.generate_user_instance(username='internal_user2', is_regular_user=False, is_admin=False, is_active=True, is_internal=True)):
        yield _