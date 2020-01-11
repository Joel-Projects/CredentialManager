import pytest, json, flask_pytest
# from flask_testing import TestCase
from tests.helpers import FlaskClient
from server import db, app, User

class IntergrationTest:

    def setup(self):
        app.test_client_class = FlaskClient
        app.config.from_object('server.config.TestingConfig')
        client = app.test_client()
        self.context = app.app_context()
        self.context.push()
        self.client = client
        self.db = db
        self.db.create_all()
        self.db.session.commit()
        with self.db.engine.connect() as sql:
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
        admin = User(username='admin', password='password', admin=True)
        notadmin = User(username='notadmin', password='password', admin=False)
        self.db.session.add(admin)
        self.db.session.add(notadmin)
        self.db.session.commit()

    def teardown(self):
        self.context.pop()
        self.db.drop_all()