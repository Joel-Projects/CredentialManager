from flask_wtf import FlaskForm
from markupsafe import text_type
from wtforms.fields import StringField, BooleanField
from wtforms.widgets import HTMLString, html_params
from wtforms_alchemy import model_form_factory, QuerySelectField
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

class HiddenFieldWithToggle(BooleanField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, **kwargs):
        hiddenObject = kwargs.pop('hiddenObject')
        targetFields = kwargs.pop('forFields')
        fields = []
        for field in targetFields:
            fields.append(f'''
                    var {field.id} = $('#{field.id}');
                    {field.id}.prop('required', checked);
                    ''')
        fields = '\n'.join(fields)
        return HTMLString(f'''
        {self.meta.render_field(self, kwargs)}
        <script>
            $("#{self.id}").click(function () {{
                var checked = $('#{self.id}').prop('checked');
                var group = $('#{hiddenObject}');
                var {self.id}_checked = 'n'
                if (checked) {{
                    {self.id}_checked = 'y'
                }};
                this.value = {self.id}_checked
                group.prop('hidden', !checked);
                {fields}
        }});
        </script>''')

class AppSelectField(QuerySelectField):

    def __init__(self, *, queryKwargs={}, **kwargs):
        self.queryKwargs = queryKwargs
        super().__init__(**kwargs)

    def _get_object_list(self):
        if self._object_list is None:
            query = (self.query if self.query is not None else self.query_factory(**self.queryKwargs))
            get_pk = self.get_pk
            self._object_list = list((text_type(get_pk(obj)), obj) for obj in query)
        return self._object_list
