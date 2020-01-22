# import json
# from server import db
# from server.models import User
# from tests.base import BaseTestCase
#
# class TestAuthBlueprint(BaseTestCase):
#
#     def test_create(self):
#         '''Test for user registration '''
#         with self.client:
#             self.loginAdminUser()
#             response = self.createUser('test', '123456')
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'success')
#             self.assertTrue(data['message'] == f"Created user: 'test' successfully!")
#             self.assertTrue(response.content_type == 'application/json')
#             self.assert_status(response, 201)
#
#     def test_login(self):
#         '''Test for user registration '''
#         with self.client:
#             user = User(username='root', password='password', admin=True)
#             db.session.add(user)
#             db.session.commit()
#             loginResponse = self.loginUser('root', 'password')
#             self.assertRedirects(loginResponse, '/dash')
#
#     def test_create_admin(self):
#         '''Test for of create user with an admin user'''
#         with self.client:
#             self.loginAdminUser()
#             createResponse = self.createUser('test', '123456', admin=True)
#             createData = json.loads(createResponse.data.decode())
#             self.assertTrue(createData['status'] == 'success')
#             self.assertTrue(createData['message'] == f"Created user: 'test' successfully!")
#             self.assertTrue(createResponse.content_type == 'application/json')
#             self.assert_status(createResponse, 201)
#
#     def test_create_non_admin(self):
#         '''Test for of create user with non-admin user'''
#         with self.client:
#             self.createTestUser('nonAdmin', '123456', False)
#
#             loginResponse = self.loginUser('nonAdmin', '123456')
#             self.assertRedirects(loginResponse, '/dash')
#
#             nonAdminCreateResponse = self.createUser('test2', '123456')
#             nonAdminCreateData = json.loads(nonAdminCreateResponse.data.decode())
#             self.assertTrue(nonAdminCreateData['status'] == 'fail')
#             self.assertTrue(nonAdminCreateData['message'] == "You're not allowed to do that!")
#             self.assert403(nonAdminCreateResponse)
#
#     def test_create_with_already_created_user(self):
#         '''Test registration with already created username'''
#         self.createTestUser('test', '123456', True)
#         with self.client:
#             response = self.createUser('test', '123456')
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'fail')
#             self.assertTrue(data['message'] == 'A user with that username already exists!')
#             self.assertTrue(response.content_type == 'application/json')
#             self.assert200(response)
#
#     def test_non_created_user_login(self):
#         '''Test for login of non-created user '''
#         with self.client:
#             loginResponse = self.loginUser('test', '123456')
#             self.assertTrue(self.assert_message_flashed('Please check your login details and try again.', 'error'))
#             self.assert403(loginResponse)
#
#     def test_created_incorrect_password_user_login(self):
#         '''Test for login of created user login '''
#         with self.client:
#             self.createTestUser('test', '123456')
#             loginResponse = self.loginUser('test', '12345')
#             self.assertTrue(self.assert_message_flashed('Please check your login details and try again.', 'error'))
#             self.assert403(loginResponse)
#
#     def test_disabled_user_login(self):
#         '''Test for login of disabled user '''
#         with self.client:
#             user = User(username='test', password='123456', admin=True, enabled=False)
#             db.session.add(user)
#             db.session.commit()
#             loginResponse = self.loginUser('test', '123456')
#             self.assertTrue(self.assert_message_flashed('Your account is disabled.', 'error'))
#             self.assert403(loginResponse)
#
#     def test_logout(self):
#         '''Test logout'''
#         with self.client:
#             # user registration
#             self.createTestUser('test', 'password')
#             response = self.client.get('/logout')
#             self.assertRedirects(response, '/login')