from app.modules.bots.models import Bot


def test_bot_check_owner(regular_user, admin_user, regularUserBot):
    bot = Bot.query.first()
    assert bot.check_owner(regular_user)
    assert not bot.check_owner(admin_user)
    assert not bot.check_owner(None)
