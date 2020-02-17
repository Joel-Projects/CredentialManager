from flask_wtf import FlaskForm
from markupsafe import text_type
from wtforms.fields import StringField, TextAreaField
from wtforms.widgets import HTMLString, html_params
from wtforms_alchemy import model_form_factory
from html import escape

from app.extensions import db

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class TextArea(object):
    """
    Renders a multi-line text area.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True
        if 'value' in kwargs:
            value = kwargs['value']
        else:
            value = field._value()
        return HTMLString(f'<textarea {html_params(name=field.name, **kwargs)}>{escape(text_type(value), quote=False)}</textarea>')

class TextAreaFieldWithDefault(StringField):
    """
    This field represents an HTML ``<textarea>`` and can be used to take
    multi-line input.
    """
    widget = TextArea()