from app.modules.database_credentials.models import DatabaseCredential


def test_database_credential_check_owner(regular_user, admin_user, regularUserDatabaseCredential):
    databaseCredential = DatabaseCredential.query.first()
    assert databaseCredential.check_owner(regular_user)
    assert not databaseCredential.check_owner(admin_user)
    assert not databaseCredential.check_owner(None)