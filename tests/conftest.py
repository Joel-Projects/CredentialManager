import pytest, json, flask_pytest
# from flask_testing import TestCase
from tests.helpers import FlaskClient
from server import db as _db, app
from server.models import User, Bot, RedditApp, RefreshToken, Sentry, Database, ApiToken


@pytest.fixture
def client():
    app.test_client_class = FlaskClient
    app.config.from_object('server.config.TestingConfig')
    client = app.test_client()
    context = app.app_context()
    context.push()

    yield client

    context.pop()

@pytest.fixture(autouse=True)
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
    # admin = User(username='admin', password='password', admin=True)
    # # notadmin = User(username='notadmin', password='password', admin=False)
    # _db.session.add(admin)
    # _db.session.add(notadmin)
    # _db.session.commit()
    yield _db

    _db.drop_all()

@pytest.fixture()
def insertTestData(db):
    # items = []
    # users = User(username='admin', password='password', admin=True), User(username='notadmin', password='password', admin=False)
    # for user in users:
    #     db.session.add(user)
    #     db.session.commit()
    #     id = user.id
    #     db.session.add(ApiToken(name=f'Bot{id}', token=(0, '12345', '123457')[id], owner=user))
    #     db.session.commit()
    #     reddit = RedditApp(app_name=f'RedditApp{id}', short_name=f'short_name{id}', app_description=f'app_description{id}', client_id=f'client_id{id}', client_secret=f'client_secret{id}', user_agent=f'user_agent{id}', app_type=f'web', redirect_uri=f'redirect_uri{id}', owner=user)
    #     db.session.add(reddit)
    #     db.session.commit()
    #     sentry = Sentry(app_name=f'sentry{id}', dsn=f'https://sentry.jesassn.org/{id}', owner=user)
    #     db.session.add(sentry)
    #     db.session.commit()
    #     database = Database(app_name=f'database{id}',database_username='database_username', database_password='database_password', owner=user)
    #     db.session.add(database)
    #     db.session.commit()
    #     db.session.add(Bot(bot_name=f'bot{id}', reddit=reddit, sentry=sentry, database=database, owner=user))
    #     db.session.commit()
     # db.session.commit()
    with open('tests/testData.sql') as f:
        sqlStatements = f.readlines()
    with db.engine.connect() as sql:
        for statement in sqlStatements:
            sql.execute(statement)

@pytest.fixture()
def loginUser(client):
    return client.post('/login', data=dict(username=username, password=password, csrf_token=client.csrf_token), content_type='application/x-www-form-urlencoded')