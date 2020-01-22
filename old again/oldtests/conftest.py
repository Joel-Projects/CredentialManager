import pytest, json
from flask_testing import TestCase
from tests.helpers import FlaskClient
from server import db as _db, app, User


@pytest.fixture
def non_admin_user(db, username, password, admin):
    user = User(username='notadmin', password='password', admin=False)
    db.session.add(user)
    db.session.commit()
    loginResponse = loginUser('notadmin', 'password')
    TestCase.assertRedirects(loginResponse, '/dash')
    return user

@pytest.fixture(scope='module')
def admin_user():
    user = User(username='admin', password='password', admin=True)
    _db.session.add(user)
    _db.session.commit()
    loginResponse = loginUser('admin', 'password')
    TestCase.assertRedirects(loginResponse, '/dash')
    return user

@pytest.fixture(scope='module')
def app():
    app.test_client_class = FlaskClient
    app.config.from_object('server.config.TestingConfig')
    client = app.test_client()
    context = app.app_context()
    context.push()

    yield client

    context.pop()

@pytest.fixture(scope='module')
def createUser(client, username, password, admin=False):
    return client.post('/api/users/create', data=dict(username=username, password=password, admin=admin, csrf_token=self.client.csrf_token), content_type='application/x-www-form-urlencoded')

@pytest.fixture(scope='module')
def loginUser(client, username, password):
    return client.post('/login', data=dict(username=username, password=password, csrf_token=client.csrf_token), content_type='application/x-www-form-urlencoded')

@pytest.fixture(scope='module')
def loginAdminUser(client):
    user = User(username='root', password='password', admin=True)
    _db.session.add(user)
    _db.session.commit()
    loginResponse = loginUser(username='root', password='password')
    TestCase.assertRedirects(loginResponse, '/dash')

@pytest.fixture(scope='module')
def createTestUser(self, username, password, admin=False):
    self.loginAdminUser()
    response = self.createUser(username, password, admin)
    data = json.loads(response.data.decode())
    self.assertTrue(data['status'] == 'success')
    self.assertTrue(data['message'] == f"Created user: '{username}' successfully!")
    self.assertTrue(response.content_type == 'application/json')
    self.assert_status(response, 201)

@pytest.fixture(scope='module')
def db():
    _db.create_all()
    _db.session.commit()
    with _db.engine.connect() as sql:
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

    yield _db  # this is where the testing happens!

    _db.drop_all()
