from datetime import datetime

from app.modules.refresh_tokens.models import RefreshToken


def test_refresh_token_check_owner(
    regular_user, admin_user, internal_user, regularUserRefreshToken
):
    refreshToken = RefreshToken.query.first()
    assert refreshToken.check_owner(regular_user)
    assert not refreshToken.check_owner(admin_user)
    assert not refreshToken.check_owner(internal_user)
    assert not refreshToken.check_owner(None)


def test_revoke(regularUserRefreshToken):
    regularUserRefreshToken.revoke()
    assert regularUserRefreshToken.revoked
    assert isinstance(regularUserRefreshToken.revoked_at, datetime)


def test_valid(regularUserRefreshToken):
    assert regularUserRefreshToken.valid
