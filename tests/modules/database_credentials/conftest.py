import pytest

from app.modules.database_credentials.models import DatabaseCredential

data = {
    "database_flavor": "postgres",
    "database_host": "localhost",
    "database_port": 5432,
    "database_username": "postgres",
    "database_password": "database_password",
    "database": "postgres",
    "use_ssh": True,
    "ssh_host": "ssh_host",
    "ssh_port": 22,
    "ssh_username": "root",
    "ssh_password": "pass",
    "use_ssh_key": True,
    "private_key": "private_key",
    "private_key_passphrase": "passphrase",
}


@pytest.fixture()
def regular_user_database_credential(temp_db_instance_helper, regular_user):
    for _ in temp_db_instance_helper(
        DatabaseCredential(
            app_name="regular_user_database_credential", owner=regular_user, **data
        )
    ):
        yield _


@pytest.fixture()
def admin_user_database_credential(temp_db_instance_helper, admin_user):
    for _ in temp_db_instance_helper(
        DatabaseCredential(
            app_name="admin_user_database_credential", owner=admin_user, **data
        )
    ):
        yield _


@pytest.fixture()
def internal_user_database_credential(temp_db_instance_helper, internal_user):
    for _ in temp_db_instance_helper(
        DatabaseCredential(
            app_name="internal_user_database_credential", owner=internal_user, **data
        )
    ):
        yield _
