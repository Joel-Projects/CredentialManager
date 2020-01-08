import json
from flask_testing import TestCase
from tests.helpers import FlaskClient
from server import db, app, User, csrf, request

class BaseTestCase(TestCase):
    """ Base Tests """

    def createUser(self, username, password, admin=False):
        return self.client.post('/api/users/create', data=dict(username=username, password=password, admin=admin, csrf_token=self.client.csrf_token), content_type='application/x-www-form-urlencoded')

    def loginUser(self, username, password):
        return self.client.post('/login', data=dict(username=username, password=password, csrf_token=self.client.csrf_token), content_type='application/x-www-form-urlencoded')

    def loginAdminUser(self):
        user = User(username='root', password='password', admin=True)
        db.session.add(user)
        db.session.commit()
        loginResponse = self.loginUser('root', 'password')
        self.assertRedirects(loginResponse, '/dash')

    def createTestUser(self, username, password, admin=False):
        self.loginAdminUser()
        response = self.createUser(username, password, admin)
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == f"Created user: '{username}' successfully!")
        self.assertTrue(response.content_type == 'application/json')
        self.assert_status(response, 201)

    def create_app(self):
        app.test_client_class = FlaskClient
        app.config.from_object('server.config.TestingConfig')
        self.client = app.test_client()
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()
        with db.engine.connect() as sql:
            sql.execute('''
            create extension if not exists pgcrypto with schema public;
            create or replace function credential_store.gen_state() returns trigger
        	language plpgsql
            as $$
            BEGIN
                IF tg_op = 'INSERT' OR tg_op = 'UPDATE' THEN
                    NEW.state = encode(public.digest(NEW.client_id, 'sha256'), 'hex');
                    RETURN NEW;
                END IF;
            END;
            $$;
    
            alter function credential_store.gen_state() owner to postgres;
            drop trigger if exists refresh_token_state_hashing_trigger on credential_store.reddit_apps;
            create trigger refresh_token_state_hashing_trigger
                before insert or update
                of client_id
                on credential_store.reddit_apps
                for each row
                execute procedure credential_store.gen_state();
            ''')

    def tearDown(self):
        db.session.remove()
        db.drop_all()