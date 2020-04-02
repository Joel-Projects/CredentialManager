from app.modules.user_verifications.models import UserVerification


def test_user_verification_check_owner(regular_user, admin_user, regularUserUserVerification):
    userVerification = UserVerification.query.first()
    assert userVerification.check_owner(regular_user)
    assert not userVerification.check_owner(admin_user)
    assert not userVerification.check_owner(None)