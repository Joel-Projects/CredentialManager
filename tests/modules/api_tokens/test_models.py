from app.modules.api_tokens.models import ApiToken


def test_api_token_check_owner(admin_user, regular_user, regularUserApiToken):
    regular_user_api_token = ApiToken.query.filter(ApiToken.owner == regular_user).first()
    assert regular_user_api_token.check_owner(regular_user)
    assert not regular_user_api_token.check_owner(None)
    assert not regular_user_api_token.check_owner(admin_user)