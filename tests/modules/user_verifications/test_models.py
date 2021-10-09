from app.modules.user_verifications.models import UserVerification


def test_user_verification_check_owner(regular_user, admin_user, regular_user_user_verification):
    user_verification = UserVerification.query.first()
    assert user_verification.check_owner(regular_user)
    assert not user_verification.check_owner(admin_user)
    assert not user_verification.check_owner(None)
