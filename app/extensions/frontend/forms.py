from html import escape

from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from markupsafe import text_type
from wtforms.fields import BooleanField, StringField
from wtforms.widgets import HTMLString, html_params
from wtforms_alchemy import QuerySelectField, model_form_factory

from app.extensions import db
from app.modules.users.models import User

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session

    def get_db_data(self):
        return {key: value for key, value in self.data.items() if value not in [None, ""]}


class TextArea(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        if "value" in kwargs:
            value = kwargs["value"]
        else:
            value = field._value()
        return HTMLString(
            f"<textarea {html_params(name=field.name, **kwargs)}>{escape(text_type(value), quote=False)}</textarea>"
        )


class TextAreaFieldWithDefault(StringField):
    widget = TextArea()


class HiddenFieldWithToggle(BooleanField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, **kwargs):
        hidden_object = kwargs.pop("hidden_object")
        target_fields = kwargs.pop("for_fields")
        shown_object = kwargs.pop("shown_object", "")
        hide_fields = kwargs.pop("hide_fields", [])
        fields = []
        for field in target_fields:
            fields.append(
                f"""
                    var {field.id} = $('#{field.id}');
                    {field.id}.prop('required', checked);
                    """
            )
        for field in hide_fields:
            fields.append(
                f"""
                    var {field.id} = $('#{field.id}');
                    {field.id}.prop('required', !checked);
                    """
            )
        fields = "\n".join(fields)
        if shown_object:
            shown_object = f"""
                    var shown_group = $('#{shown_object}');
                    shown_group.prop('hidden', checked);
                    """
        return HTMLString(
            f"""
        {self.meta.render_field(self, kwargs)}
        <script>
            $("#{self.id}").click(function () {{
                var checked = $('#{self.id}').prop('checked');
                var group = $('#{hidden_object}');
                var {self.id}_checked = 'n'
                if (checked) {{
                    {self.id}_checked = 'y'
                }};
                this.value = {self.id}_checked
                group.prop('hidden', !checked);
                {shown_object}
                {fields}
        }});
        </script>"""
        )


class ModelSelectField(QuerySelectField):
    def __init__(self, *, query_kwargs={}, **kwargs):
        self.query_kwargs = query_kwargs
        super().__init__(**kwargs)

    def _get_object_list(self):
        if self._object_list is None:
            query = self.query if self.query is not None else self.query_factory(**self.query_kwargs)
            get_pk = self.get_pk
            self._object_list = list((text_type(get_pk(obj)), obj) for obj in query)
        return self._object_list


def owners(current_user):
    from app.modules.users.models import User

    if current_user.is_internal:
        return User.query
    else:
        return User.query.filter_by(internal=False)


def check_model_owner(owner):
    if request.method == "POST" and (current_user.is_admin or current_user.is_internal):
        owner_id = int(request.form.get("owner", current_user.id))
        owner = User.query.get(owner_id)
    elif request.path.startswith("/bots/"):
        owner = request.view_args["bot"].owner
    elif request.path.startswith("/user_verifications/"):
        owner = request.view_args["user_verification"].owner
    return owner


def reddit_apps(owner):
    owner = check_model_owner(owner)
    return owner.reddit_apps.filter_by(enabled=True)
