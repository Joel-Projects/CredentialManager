from app.modules.database_credentials.models import DatabaseCredential


def test_database_credential_check_owner(
    regular_user, admin_user, regular_user_database_credential
):
    database_credential = DatabaseCredential.query.first()
    assert database_credential.check_owner(regular_user)
    assert not database_credential.check_owner(admin_user)
    assert not database_credential.check_owner(None)
