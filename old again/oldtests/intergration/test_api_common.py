from server import db
from server.models import Bot, RedditApp, RefreshToken, Sentry, Database, ApiToken
from tests.base import BaseTestCase

def insertTestData():
    with open('tests/testData.sql') as f:
        sqlStatements = f.read()
    with db.engine.connect() as sql:
        sql.execute(sqlStatements)

class TestToggle(BaseTestCase):

    def test_disable_admin_not_owner(self):
        insertTestData()
        self.loginUser('root', 'password')
        response = self.client.post('/api/toggle', data={'item_type': 'bot', 'id': 2, 'enabled': False})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertFalse(bot.enabled)

    def test_disable_admin_not_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/toggle', data={'key': '12345', 'item_type': 'bot', 'id': 2, 'enabled': False})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertFalse(bot.enabled)

    def test_disable_admin_owner(self):
        insertTestData()
        self.loginUser('root', 'password')
        response = self.client.post('/api/toggle', data={'item_type': 'bot', 'id': 1, 'enabled': False})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertFalse(bot.enabled)

    def test_disable_admin_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/toggle', data={'key': '12345', 'item_type': 'bot', 'id': 1, 'enabled': False})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertFalse(bot.enabled)

    def test_disable_not_admin_not_owner(self):
        insertTestData()
        self.loginUser('notadmin', 'password')
        response = self.client.post('/api/toggle', data={'item_type': 'bot', 'id': 1, 'enabled': False})
        self.assert_status(response, 403)

    def test_disable_not_admin_not_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/toggle', data={'key': '123457', 'item_type': 'bot', 'id': 1, 'enabled': False})
        self.assert_status(response, 403)

    def test_disable_not_admin_owner(self):
        insertTestData()
        self.loginUser('notadmin', 'password')
        response = self.client.post('/api/toggle', data={'item_type': 'bot', 'id': 2, 'enabled': False})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertFalse(bot.enabled)

    def test_disable_not_admin_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/toggle', data={'key': '123457', 'item_type': 'bot', 'id': 2, 'enabled': False})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertFalse(bot.enabled)

    def test_enable_admin_not_owner(self):
        insertTestData()
        self.loginUser('root', 'password')
        response = self.client.post('/api/toggle', data={'item_type': 'bot', 'id': 2, 'enabled': True})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertTrue(bot.enabled)

    def test_enable_admin_not_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/toggle', data={'key': '12345', 'item_type': 'bot', 'id': 2, 'enabled': True})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertTrue(bot.enabled)

    def test_enable_admin_owner(self):
        insertTestData()
        self.loginUser('root', 'password')
        response = self.client.post('/api/toggle', data={'item_type': 'bot', 'id': 1, 'enabled': True})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertTrue(bot.enabled)

    def test_enable_admin_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/toggle', data={'key': '12345', 'item_type': 'bot', 'id': 1, 'enabled': True})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertTrue(bot.enabled)

    def test_enable_not_admin_not_owner(self):
        insertTestData()
        self.loginUser('notadmin', 'password')
        response = self.client.post('/api/toggle', data={'item_type': 'bot', 'id': 1, 'enabled': True})
        self.assert_status(response, 403)

    def test_enable_not_admin_not_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/toggle', data={'key': '123457', 'item_type': 'bot', 'id': 1, 'enabled': True})
        self.assert_status(response, 403)

    def test_enable_not_admin_owner(self):
        insertTestData()
        self.loginUser('notadmin', 'password')
        response = self.client.post('/api/toggle', data={'item_type': 'bot', 'id': 2, 'enabled': True})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertTrue(bot.enabled)

    def test_enable_not_admin_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/toggle', data={'key': '123457', 'item_type': 'bot', 'id': 2, 'enabled': True})
        self.assert_status(response, 202)
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertTrue(bot.enabled)

class TestDelete(BaseTestCase):

    def test_delete_admin_not_owner(self):
        insertTestData()
        self.loginUser('root', 'password')
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertIsNotNone(bot)
        response = self.client.post('/api/delete', data={'item_type': 'bot', 'id': 2, 'cascade': True})
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assert_status(response, 202)
        self.assertIsNone(bot)

    def test_delete_admin_not_owner_with_key(self):
        insertTestData()
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertIsNotNone(bot)
        response = self.client.post('/api/delete', data={'key': '12345', 'item_type': 'bot', 'id': 2, 'cascade': True})
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertIsNone(bot)
        self.assert_status(response, 202)

    def test_delete_admin_owner(self):
        insertTestData()
        self.loginUser('root', 'password')
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertIsNotNone(bot)
        response = self.client.post('/api/delete', data={'item_type': 'bot', 'id': 1, 'cascade': True})
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertIsNone(bot)
        self.assert_status(response, 202)

    def test_delete_admin_owner_with_key(self):
        insertTestData()
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertIsNotNone(bot)
        response = self.client.post('/api/delete', data={'key': '12345', 'item_type': 'bot', 'id': 1, 'cascade': True})
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertIsNone(bot)
        self.assert_status(response, 202)

    def test_delete_not_admin_not_owner(self):
        insertTestData()
        self.loginUser('notadmin', 'password')
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertIsNotNone(bot)
        response = self.client.post('/api/delete', data={'item_type': 'bot', 'id': 1, 'cascade': True})
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertIsNotNone(bot)
        self.assert_status(response, 403)

    def test_delete_not_admin_not_owner_with_key(self):
        insertTestData()
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertIsNotNone(bot)
        response = self.client.post('/api/delete', data={'key': '123457', 'item_type': 'bot', 'id': 1, 'cascade': True})
        bot = Bot.query.filter(Bot.id == 1).first()
        self.assertIsNotNone(bot)
        self.assert_status(response, 403)

    def test_delete_not_admin_owner(self):
        insertTestData()
        self.loginUser('notadmin', 'password')
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertIsNotNone(bot)
        response = self.client.post('/api/delete', data={'item_type': 'bot', 'id': 2, 'cascade': True})
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertIsNone(bot)
        self.assert_status(response, 202)

    def test_delete_not_admin_owner_with_key(self):
        insertTestData()
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertIsNotNone(bot)
        response = self.client.post('/api/delete', data={'key': '123457', 'item_type': 'bot', 'id': 2, 'cascade': True})
        bot = Bot.query.filter(Bot.id == 2).first()
        self.assertIsNone(bot)
        self.assert_status(response, 202)

class TestUpdate(BaseTestCase):

    def test_update_admin_not_owner(self):
        insertTestData()
        self.loginUser('root', 'password')
        response = self.client.post('/api/update', data={'item_type': 'bot', 'id': 2, 'data': {'bot_name': 'newbotname2'}})
        bot = Bot.query.filter(Bot.id == 2).first()
        newName = bot.bot_name
        self.assert_status(response, 202)
        self.assertEqual(newName, 'newbotname2')

    def test_update_admin_not_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/update', data={'key': '12345', 'item_type': 'bot', 'id': 2, 'data': {'bot_name': 'newbotname2'}})
        bot = Bot.query.filter(Bot.id == 2).first()
        newName = bot.bot_name
        self.assert_status(response, 202)
        self.assertEqual(newName, 'newbotname2')

    def test_update_admin_owner(self):
        insertTestData()
        self.loginUser('root', 'password')
        response = self.client.post('/api/update', data={'item_type': 'bot', 'id': 1, 'data': {'bot_name': 'newbotname1'}})
        bot = Bot.query.filter(Bot.id == 1).first()
        newName = bot.bot_name
        self.assert_status(response, 202)
        self.assertEqual(newName, 'newbotname1')

    def test_update_admin_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/update', data={'key': '12345', 'item_type': 'bot', 'id': 1, 'data': {'bot_name': 'newbotname1'}})
        bot = Bot.query.filter(Bot.id == 1).first()
        newName = bot.bot_name
        self.assert_status(response, 202)
        self.assertEqual(newName, 'newbotname1')

    def test_update_not_admin_not_owner(self):
        insertTestData()
        self.loginUser('notadmin', 'password')
        bot = Bot.query.filter(Bot.id == 1).first()
        oldName = bot.bot_name
        response = self.client.post('/api/update', data={'item_type': 'bot', 'id': 1, 'data': {'bot_name': 'newbotname1'}})
        bot = Bot.query.filter(Bot.id == 1).first()
        newName = bot.bot_name
        self.assertEqual(oldName, newName)
        self.assert_status(response, 403)

    def test_update_not_admin_not_owner_with_key(self):
        insertTestData()
        bot = Bot.query.filter(Bot.id == 1).first()
        oldName = bot.bot_name
        response = self.client.post('/api/update', data={'key': '123457', 'item_type': 'bot', 'id': 1, 'data': {'bot_name': 'newbotname1'}})
        bot = Bot.query.filter(Bot.id == 1).first()
        newName = bot.bot_name
        self.assertEqual(oldName, newName)
        self.assert_status(response, 403)

    def test_update_not_admin_owner(self):
        insertTestData()
        self.loginUser('notadmin', 'password')
        response = self.client.post('/api/update', data={'item_type': 'bot', 'id': 2, 'data': {'bot_name': 'newbotname2'}})
        bot = Bot.query.filter(Bot.id == 2).first()
        newName = bot.bot_name
        self.assert_status(response, 202)
        self.assertEqual(newName, 'newbotname2')

    def test_update_not_admin_owner_with_key(self):
        insertTestData()
        response = self.client.post('/api/update', data={'key': '123457', 'item_type': 'bot', 'id': 2, 'data': {'bot_name': 'newbotname2'}})
        bot = Bot.query.filter(Bot.id == 2).first()
        newName = bot.bot_name
        self.assert_status(response, 202)
        self.assertEqual(newName, 'newbotname2')