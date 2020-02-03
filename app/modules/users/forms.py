from flask_login import current_user
from wtforms.fields import BooleanField, SubmitField, Field
from wtforms.meta import DefaultMeta
from wtforms.validators import Optional, url
from wtforms.widgets import HTMLString

from app.extensions import ModelForm
from .models import User

# class HiddenFieldCheckboxMeta(DefaultMeta):
#     """
#     This is the default Meta class which defines all the default values and
#     therefore also the 'API' of the class Meta interface.
#     """
#
#     # -- Basic form primitives
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     # def render_field(self, field, ):
#     #     """
#     #     render_field allows customization of how widget rendering is done.
#     #
#     #     The default implementation calls ``field.widget(field, **render_kw)``
#     #     """
#     #     other_kw = getattr(field, 'render_kw', None)
#     #     if other_kw is not None:
#     #         render_kw = dict(other_kw)
#     #     fieldHtml = field.widget(field)
#     #     print()
#     #     return


class HiddenFieldWithToggle(BooleanField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, **kwargs):
        """
        Render this field as HTML, using keyword args as additional attributes.

        This delegates rendering to
        :meth:`meta.render_field <wtforms.meta.DefaultMeta.render_field>`
        whose default behavior is to call the field's widget, passing any
        keyword arguments from this call along to the widget.

        In all of the WTForms HTML widgets, keyword arguments are turned to
        HTML attributes, though in theory a widget is free to do anything it
        wants with the supplied keyword arguments, and widgets don't have to
        even do anything related to HTML.
        """
        hiddenObject = kwargs.pop('hiddenObject')
        targetField = kwargs.pop('forField').id
        return HTMLString(f'''
{self.meta.render_field(self, kwargs)}
<script>
    $("#{self.id}").click(function () {{
        var checked = $('#{self.id}').prop('checked');
        var group = $('#{hiddenObject}');
        var field = $('#{targetField}');
        group.prop('hidden', !checked);
        field.prop('required', checked);
}});
</script>''')
        # return finalHtml

class UserForm(ModelForm):
    class Meta:
        model = User
        only = ['username', 'password', 'default_redirect_uri']

    is_admin = BooleanField('Admin?')
    is_internal = BooleanField('Internal?')
    is_regular_user = BooleanField('Regular User?')
    is_active = BooleanField('Active?')

    # submit = SubmitField('Create')
    # create_new = SubmitField('Create and New')

class EditUserForm(ModelForm):

    class Meta:
        model = User
        only = ['id', 'username', 'password', 'default_redirect_uri']
        field_args = {
            'id': {'validators': [Optional()]},
            'password': {'validators': [Optional()]},
            # 'default_redirect_uri': {'validators': [url()]}
        }

    updatePassword = HiddenFieldWithToggle('Update Password?')
    is_admin = BooleanField('Admin?')
    is_internal = BooleanField('Internal?')
    is_regular_user = BooleanField('Regular User?')
    is_active = BooleanField('Active?')