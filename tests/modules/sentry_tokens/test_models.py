from app.modules.sentry_tokens.models import SentryToken


def test_sentry_token_check_owner(regular_user, admin_user, regularUserSentryToken):
    sentryToken = SentryToken.query.first()
    assert sentryToken.check_owner(regular_user)
    assert not sentryToken.check_owner(admin_user)
    assert not sentryToken.check_owner(None)
