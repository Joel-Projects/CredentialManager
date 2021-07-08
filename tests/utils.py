import json
from base64 import b64encode
from contextlib import contextmanager
from datetime import datetime, timezone

from flask import Response, message_flashed, template_rendered
from flask.testing import FlaskClient
from flask_sqlalchemy import Model
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy_utils import Choice
from werkzeug.utils import cached_property

from app.modules.users.models import User


class AutoAuthFlaskClient(FlaskClient):
    """
    A helper FlaskClient class with a useful for testing ``login`` context
    manager.
    """

    def __init__(self, *args, **kwargs):
        super(AutoAuthFlaskClient, self).__init__(*args, **kwargs)
        self._user = None

    @contextmanager
    def login(self, user):

        with self.application.test_request_context():
            if user:
                self.post(
                    "/login",
                    data={"username": user.username, "password": user.password_secret},
                    follow_redirects=True,
                )
            self._user = user
            yield self
            self.post("/logout", follow_redirects=True)
            self._user = None

    def open(self, *args, **kwargs):
        from flask_login import current_user

        if current_user and current_user.is_authenticated:
            self._user = current_user
        if self._user is not None:
            headers = {
                "Authorization": f'Basic {b64encode(f"{self._user.username}:password".encode()).decode("ascii")}'
            }
            kwargs["headers"] = headers

        return super(AutoAuthFlaskClient, self).open(*args, **kwargs)


class JSONResponse(Response):
    """
    A Response class with extra useful helpers, i.e. ``.json`` property.
    """

    @cached_property
    def json(self):
        return json.loads(self.get_data(as_text=True))


def generate_user_instance(
    user_id=None,
    username="username",
    password=None,
    default_settings=None,
    created=None,
    updated=None,
    is_active=True,
    is_regular_user=True,
    is_admin=False,
    is_internal=False,
):
    """
    Returns:
        user_instance (User) - an not committed to DB instance of a User model.
    """

    if default_settings is None:
        default_settings = {}
    from app.modules.users.models import User

    if password is None:
        password = f"{username}_password"
    user_instance = User(
        id=user_id,
        username=username,
        password=password,
        default_settings=default_settings,
        created=created or datetime.now(),
        updated=updated or datetime.now(),
        is_active=is_active,
        is_regular_user=is_regular_user,
        is_admin=is_admin,
        is_internal=is_internal,
    )
    user_instance.password_secret = password
    return user_instance


def assert_valid_response_content_type(response, delete=False):
    if delete:
        assert response.content_type == "text/html; charset=utf-8"
        assert response.content_length is None
    else:
        assert response.content_type == "application/json"
        assert isinstance(response.json, dict)


def assert_success(response, owner, model, schema, delete_item_id=None):
    assert_valid_response_content_type(response, delete=delete_item_id)
    if delete_item_id:
        assert response.status_code == 204
        item = model.query.get(delete_item_id)
        assert item is None
    else:
        assert response.status_code == 200
        set_to_test = set(schema.Meta.fields)
        if "enabled" in set_to_test:
            set_to_test.remove("enabled")
        assert set(response.json.keys()) >= set_to_test
        for field in set_to_test:
            if response.json[field] and not field == "resource_type":
                if isinstance(getattr(model, field), property):
                    assert isinstance(response.json[field], bool)
                elif not isinstance(
                    getattr(model, field), InstrumentedAttribute
                ):  # pragma: no cover
                    if getattr(model, field).type.python_type == datetime:
                        assert isinstance(response.json[field], str)
                    else:
                        assert isinstance(
                            response.json[field], getattr(model, field).type.python_type
                        )
        created_item = model.query.filter_by(id=response.json["id"]).first()
        assert created_item is not None
        if "owner_id" in response.json:
            assert response.json["owner_id"] == owner.id
        for field in set_to_test:
            if (
                not field == "resource_type"
                and response.json[field]
                and not field == "enabled"
            ):
                if isinstance(getattr(created_item, field), datetime):
                    assert (
                        response.json[field]
                        == datetime.astimezone(
                            getattr(created_item, field), timezone.utc
                        ).isoformat()
                    )
                elif isinstance(getattr(created_item, field), Choice):
                    assert response.json[field] == getattr(created_item, field).code
                elif issubclass(type(getattr(created_item, field)), Model):
                    for key, value in response.json[field].items():
                        if key != "resource_type":
                            if isinstance(
                                getattr(getattr(created_item, field), key), Choice
                            ):
                                assert (
                                    getattr(getattr(created_item, field), key).code
                                    == value
                                )
                            else:
                                assert (
                                    getattr(getattr(created_item, field), key) == value
                                )
                else:
                    if field != "resource_type":
                        assert response.json[field] == getattr(created_item, field)


def item_not_created(model, *, login_as):
    items = model.query.all()
    if model._sa_class_manager.class_ == User:
        created_user = User.query.filter(User.id != login_as.id).first()
        assert created_user is None
    else:
        assert len(items) == 0


def item_not_modified(model, old_item):
    item = model.query.get(old_item.id)
    assert item == old_item


def item_not_deleted(model, old_item):
    item = model.query.get(old_item.id)
    assert item is not None


def __assert_response_error(
    response, code, message, action="created", keys=None, message_attrs=None, **kwargs
):
    if keys is None:
        keys = {"status", "message"}
    assert response.status_code == code
    assert response.content_type == "application/json"
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) >= keys
    assert response.json["message"] == message
    if "messages" in response.json:
        for message_attr, message in message_attrs:
            assert response.json["messages"][message_attr] == message
    if action == "patch":
        item_not_modified(
            **{k: v for k, v in kwargs.items() if k in ["model", "old_item"]}
        )
    elif action == "created":
        item_not_created(
            **{k: v for k, v in kwargs.items() if k in ["model", "login_as"]}
        )
    elif action == "deleted":
        item_not_deleted(
            **{k: v for k, v in kwargs.items() if k in ["model", "old_item"]}
        )


def assert401(response, model, *, login_as, action="None"):
    __assert_response_error(
        response,
        401,
        "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.",
        model=model,
        login_as=login_as,
        action=action,
    )


def assert403(
    response, model, *, action=None, login_as=None, internal=False, old_item=None
):
    if internal:
        __assert_response_error(
            response,
            403,
            "You don't have the permission to access the requested resource.",
            action=action,
            model=model,
            login_as=login_as,
            old_item=old_item,
        )
    else:
        __assert_response_error(
            response,
            403,
            f"You don't have the permission to create {model._display_name_plural} for other users.",
            action=action,
            model=model,
            login_as=login_as,
            old_item=old_item,
        )


def assert409(response, model, message, login_as, **kwargs):
    __assert_response_error(
        response, 409, message=message, model=model, login_as=login_as, **kwargs
    )


def assert422(response, model, message_attrs, *, login_as=None, **kwargs):
    __assert_response_error(
        response,
        422,
        "The request was well-formed but was unable to be followed due to semantic errors.",
        model=model,
        login_as=login_as,
        keys={"status", "message", "messages"},
        message_attrs=message_attrs,
        **kwargs,
    )


@contextmanager
def captured_templates(app):
    recorded = {}

    def record_template(sender, template, context, **extra):
        if not "templates" in recorded:
            recorded["templates"] = []
        recorded["templates"].append((template, context))

    def record_flash(sender, message, category, **extra):
        if not "flashes" in recorded:
            recorded["flashes"] = []
        recorded["flashes"].append((message, category))

    template_rendered.connect(record_template, app)
    message_flashed.connect(record_flash, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record_template, app)
        message_flashed.disconnect(record_flash, app)


def assert_rendered_template(items, template_name):
    templates = items["templates"]
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == template_name


def assert_message_flashed(items, message, category):
    flashes = items["flashes"]
    assert len(flashes) == 1
    flashed_message, flashed_category = flashes[0]
    assert flashed_message == message
    assert flashed_category == category


def change_owner(db, new_owner, item):
    item.owner = new_owner
    db.session.merge(item)
    return item


def assert_created(item, data):
    assert item is not None
    assert item.id == 1
    for key, value in data.items():
        if issubclass(type(getattr(item, key)), Model):
            assert str(getattr(item, key).id) == value
        else:
            assert getattr(item, key) == value


def assert_modified(data, model):
    for key, value in data.items():
        if key in dir(model):
            if key == "enabled":
                value = "y" == value
            if issubclass(type(getattr(model, key)), Model):
                assert str(getattr(model, key).id) == value
            else:
                assert getattr(model, key) == value
