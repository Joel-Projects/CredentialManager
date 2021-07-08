from app.modules.sentry_tokens.models import SentryToken


def test_sentry_token_check_owner(regular_user, admin_user, regular_user_sentry_token):
    sentry_token = SentryToken.query.first()
    assert sentry_token.check_owner(regular_user)
    assert not sentry_token.check_owner(admin_user)
    assert not sentry_token.check_owner(None)
