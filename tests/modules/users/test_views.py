import pytest
from flask_testing import TestCase
from flask_login import login_user

@pytest.mark.usefixtures('flask_app_client')
class TestUsers(TestCase):

    def create_app(self):
        self.app.config['TESTING'] = True
        return self.app

    @pytest.mark.usefixtures('regularUserInstance')
    def test_root_regular_user(self):
        login_user(self.user)
        response = self.client.get('/users')
        assert response.status_code == 403
        assert response.mimetype == 'text/html'
        assert self.assertTemplateUsed('errors/403.html')

        # todo add post

    @pytest.mark.usefixtures('adminUserInstance')
    def test_root_admin_user(self):
        login_user(self.user)
        response = self.client.get('/users')
        assert response.status_code == 200
        assert response.mimetype == 'text/html'
        assert self.assertTemplateUsed('users.html')

        # todo add post

    @pytest.mark.usefixtures('internalUserInstance')
    def test_root_internal_user(self):
        login_user(self.user)
        response = self.client.get('/users')
        assert response.status_code == 200
        assert response.mimetype == 'text/html'
        assert self.assertTemplateUsed('users.html')

        # todo add post

    @pytest.mark.usefixtures('regularUserInstance', 'regular_user')
    def test_user_detail_regular_user(self):
        login_user(self.user)
        response = self.client.get(f'/u/{self.dbUser.username}')
        assert response.status_code == 403
        assert response.mimetype == 'text/html'
        assert self.assertTemplateUsed('errors/403.html')

    @pytest.mark.usefixtures('adminUserInstance', 'admin_user')
    def test_user_detail_admin_user(self):
        login_user(self.user)
        response = self.client.get(f'/u/{self.dbUser.username}')
        assert response.status_code == 200
        assert response.mimetype == 'text/html'
        assert self.assertTemplateUsed('edit_user.html')

    @pytest.mark.usefixtures('internalUserInstance', 'internal_user')
    def test_user_detail_internal_user(self):
        login_user(self.user)
        response = self.client.get(f'/u/{self.dbUser.username}')
        assert response.status_code == 200
        assert response.mimetype == 'text/html'
        assert self.assertTemplateUsed('edit_user.html')