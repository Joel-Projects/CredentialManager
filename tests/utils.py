import json
from base64 import b64encode
from contextlib import contextmanager
from datetime import datetime, timezone

from flask import Response, message_flashed, template_rendered
from flask.testing import FlaskClient
from flask_sqlalchemy import Model
from sqlalchemy_utils import Choice
from werkzeug.utils import cached_property
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.modules.users.models import User


class AutoAuthFlaskClient(FlaskClient):
    '''
    A helper FlaskClient class with a useful for testing ``login`` context
    manager.
    '''

    def __init__(self, *args, **kwargs):
        super(AutoAuthFlaskClient, self).__init__(*args, **kwargs)
        self._user = None

    @contextmanager
    def login(self, user):

        with self.application.test_request_context():
            if user:
                self.post('/login', data={'username': user.username, 'password': user.password_secret}, follow_redirects=True)
            self._user = user
            yield self
            self.post('/logout', follow_redirects=True)
            self._user = None

    def open(self, *args, **kwargs):
        from flask_login import current_user
        if current_user and current_user.is_authenticated:
            self._user = current_user
        if self._user is not None:
            headers = {'Authorization': f'Basic {b64encode(f"{self._user.username}:password".encode()).decode("ascii")}'}
            kwargs['headers'] = headers

        return super(AutoAuthFlaskClient, self).open(*args, **kwargs)

class JSONResponse(Response):
    '''
    A Response class with extra useful helpers, i.e. ``.json`` property.
    '''

    @cached_property
    def json(self):
        return json.loads(self.get_data(as_text=True))

def generateUserInstance(user_id=None, username='username', password=None, default_settings=None, created=None, updated=None, is_active=True, is_regular_user=True, is_admin=False, is_internal=False):
    '''
    Returns:
        user_instance (User) - an not committed to DB instance of a User model.
    '''

    if default_settings is None:
        default_settings = {}
    from app.modules.users.models import User
    if password is None:
        password = f'{username}_password'
    user_instance = User(id=user_id, username=username, password=password, default_settings=default_settings, created=created or datetime.now(), updated=updated or datetime.now(), is_active=is_active, is_regular_user=is_regular_user, is_admin=is_admin, is_internal=is_internal)
    user_instance.password_secret = password
    return user_instance

def assertValidResponseContentType(response, delete=False):
    if delete:
        assert response.content_type == 'text/html; charset=utf-8'
        assert response.content_length is None
    else:
        assert response.content_type == 'application/json'
        assert isinstance(response.json, dict)

def assertSuccess(response, owner, model, schema, deleteItemId=None):
    assertValidResponseContentType(response, delete=deleteItemId)
    if deleteItemId:
        assert response.status_code == 204
        item = model.query.get(deleteItemId)
        assert item is None
    else:
        assert response.status_code == 200
        assert set(response.json.keys()) >= set(schema.Meta.fields)
        for field in schema.Meta.fields:
            if response.json[field] and not field == 'resource_type':
                if isinstance(getattr(model, field), property):
                    assert isinstance(response.json[field], bool)
                elif not isinstance(getattr(model, field), InstrumentedAttribute): # pragma: no cover
                    if getattr(model, field).type.python_type == datetime:
                        assert isinstance(response.json[field], str)
                    else:
                        assert isinstance(response.json[field], getattr(model, field).type.python_type)
        createdItem = model.query.filter_by(id=response.json['id']).first()
        assert createdItem is not None
        if 'owner_id' in response.json:
            assert response.json['owner_id'] == owner.id
        for field in schema.Meta.fields:
            if not field == 'resource_type' and response.json[field]:
                if isinstance(getattr(createdItem, field), datetime):
                    assert response.json[field] == datetime.astimezone(getattr(createdItem, field), timezone.utc).isoformat()
                elif isinstance(getattr(createdItem, field), Choice):
                    assert response.json[field] == getattr(createdItem, field).value
                elif issubclass(type(getattr(createdItem, field)), Model):
                    for key, value in response.json[field].items():
                        if key != 'resource_type':
                            if isinstance(getattr(getattr(createdItem, field), key), Choice):
                                assert getattr(getattr(createdItem, field), key).value == value
                            else:
                                assert getattr(getattr(createdItem, field), key) == value
                else:
                    if field != 'resource_type':
                        assert response.json[field] == getattr(createdItem, field)

def itemNotCreated(model, *, loginAs):
    items = model.query.all()
    if model._sa_class_manager.class_ == User:
        createdUser = User.query.filter(User.id != loginAs.id).first()
        assert createdUser is None
    else:
        assert len(items) == 0

def itemNotModified(model, oldItem):
    item = model.query.get(oldItem.id)
    assert item == oldItem

def itemNotDeleted(model, oldItem):
    item = model.query.get(oldItem.id)
    assert item is not None

def __assertResponseError(response, code, message, action='created', keys=None, messageAttrs=None, **kwargs):
    if keys is None:
        keys = {'status', 'message'}
    assert response.status_code == code
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= keys
    assert response.json['message'] == message
    if 'messages' in response.json:
        for messageAttr, message in messageAttrs:
            assert response.json['messages'][messageAttr] == message
    if action == 'patch':
        itemNotModified(**{k: v for k, v in kwargs.items() if k in ['model', 'oldItem']})
    elif action == 'created':
        itemNotCreated(**{k: v for k, v in kwargs.items() if k in ['model', 'loginAs']})
    elif action == 'deleted':
        itemNotDeleted(**{k: v for k, v in kwargs.items() if k in ['model', 'oldItem']})

def assert401(response, model, *, loginAs, action='None'):
    __assertResponseError(response, 401, "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.", model=model, loginAs=loginAs, action=action)

def assert403(response, model, *, action=None, loginAs=None, internal=False, oldItem=None):
    if internal:
        __assertResponseError(response, 403, "You don't have the permission to access the requested resource.", action=action, model=model, loginAs=loginAs, oldItem=oldItem)
    else:
        __assertResponseError(response, 403, f"You don't have the permission to create {model._displayNamePlural} for other users.", action=action, model=model, loginAs=loginAs, oldItem=oldItem)

def assert409(response, model, message, loginAs, **kwargs):
    __assertResponseError(response, 409, message=message, model=model, loginAs=loginAs, **kwargs)

def assert422(response, model, messageAttrs, *, loginAs=None, **kwargs):
    __assertResponseError(response, 422, 'The request was well-formed but was unable to be followed due to semantic errors.', model=model, loginAs=loginAs, keys={'status', 'message', 'messages'}, messageAttrs=messageAttrs, **kwargs)

@contextmanager
def captured_templates(app):
    recorded = {}

    def recordTemplate(sender, template, context, **extra):
        if not 'templates' in recorded:
            recorded['templates'] = []
        recorded['templates'].append((template, context))

    def recordFlash(sender, message, category, **extra):
        if not 'flashes' in recorded:
            recorded['flashes'] = []
        recorded['flashes'].append((message, category))

    template_rendered.connect(recordTemplate, app)
    message_flashed.connect(recordFlash, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(recordTemplate, app)
        message_flashed.disconnect(recordFlash, app)

def assertRenderedTemplate(items, templateName):
    templates = items['templates']
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == templateName

def assertMessageFlashed(items, message, category):
    flashes = items['flashes']
    assert len(flashes) == 1
    flashedMessage, flashedCategory = flashes[0]
    assert flashedMessage == message
    assert flashedCategory == category

def changeOwner(db, newOwner, item):
    item.owner = newOwner
    db.session.merge(item)
    return item

def assertCreated(item, data):
    assert item is not None
    assert item.id == 1
    for key, value in data.items():
        if issubclass(type(getattr(item, key)), Model):
            assert str(getattr(item, key).id) == value
        else:
            assert getattr(item, key) == value

def assertModified(data, model):
    for key, value in data.items():
        if key in dir(model):
            if key == 'enabled':
                value = 'y' == value
            if issubclass(type(getattr(model, key)), Model):
                assert str(getattr(model, key).id) == value
            else:
                assert getattr(model, key) == value
