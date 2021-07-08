from datetime import datetime

from app.modules.refresh_tokens.models import RefreshToken


def test_refresh_token_check_owner(
    regular_user, admin_user, internal_user, regular_user_refresh_token
):
    refresh_token = RefreshToken.query.first()
    assert refresh_token.check_owner(regular_user)
    assert not refresh_token.check_owner(admin_user)
    assert not refresh_token.check_owner(internal_user)
    assert not refresh_token.check_owner(None)


def test_revoke(regular_user_refresh_token):
    regular_user_refresh_token.revoke()
    assert regular_user_refresh_token.revoked
    assert isinstance(regular_user_refresh_token.revoked_at, datetime)


def test_valid(regular_user_refresh_token):
    assert regular_user_refresh_token.valid
