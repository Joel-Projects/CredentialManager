import gc
import unittest
import socketserver
from urllib.parse import urlparse, urljoin

from werkzeug.utils import cached_property

from flask import json_available, templating, template_rendered, message_flashed

_is_message_flashed = True

from flask import json

try:
    import blinker

    _is_signals = True
except ImportError:  # pragma: no cover
    _is_signals = False


class ContextVariableDoesNotExist(Exception):
    pass


class JsonResponseMixin(object):

    @cached_property
    def json(self):
        if not json_available:  # pragma: no cover
            raise NotImplementedError
        return json.loads(self.data)


def _make_test_response(response_class):
    class TestResponse(response_class, JsonResponseMixin):
        pass

    return TestResponse


def _empty_render(template, context, app):
    '''
    Used to monkey patch the render_template flask method when
    the render_templates property is set to False in the TestCase
    '''
    template_rendered.send(app, template=template, context=context)


class FlaskTester:

    def __init__(self, client):
        self.client = client
        self.app = self.client.application

    def __enter__(self):

        self.templates = []
        self.flashed_messages = []

        template_rendered.connect(self._add_template)

        message_flashed.connect(self._add_flash_message)
        return self

    def _add_flash_message(self, app, message, category):
        self.flashed_messages.append((message, category))

    def _add_template(self, app, template, context):
        if len(self.templates) > 0:
            self.templates = []
        self.templates.append((template, context))

    def __exit__(self, *args, **kwargs):
        # if getattr(self, '_ctx', None) is not None:
        #     self._ctx.pop()
        #     del self._ctx
        #
        # if getattr(self, 'app', None) is not None:
        #     if getattr(self, '_orig_response_class', None) is not None:
        #         self.app.response_class = self._orig_response_class
        #     del self.app
        #
        # if hasattr(self, 'client'):
        #     del self.client
        #
        # if hasattr(self, 'templates'):
        #     del self.templates
        #
        # if hasattr(self, 'flashed_messages'):
        #     del self.flashed_messages
        #
        # if _is_signals:
        #     template_rendered.disconnect(self._add_template)
        #
        #     if _is_message_flashed:
        #         message_flashed.disconnect(self._add_flash_message)
        #
        # if hasattr(self, '_original_template_render'):
        #     templating._render = self._original_template_render
        pass

    def assertTemplateUsed(self, name, tmpl_name_attribute='name'):
        '''
        Checks if a given template is used in the request.
        Only works if your version of Flask has signals
        support (0.6+) and blinker is installed.
        If the template engine used is not Jinja2, provide
        ``tmpl_name_attribute`` with a value of its `Template`
        class attribute name which contains the provided ``name`` value.

        :versionadded: 0.2
        :param name: template name
        :param tmpl_name_attribute: template engine specific attribute name
        '''
        used_templates = []

        for template, context in self.templates:
            if getattr(template, tmpl_name_attribute) == name:
                return True

            used_templates.append(template)

        raise AssertionError(f'Template {name} not used. Templates were used: {" ".join(repr(used_templates))}')

    def assertRedirects(self, response, location, message=None):
        '''
        Checks if response is an HTTP redirect to the
        given location.

        :param response: Flask response
        :param location: relative URL path to SERVER_NAME or an absolute URL
        '''
        parts = urlparse(location)

        if parts.netloc:
            expected_location = location
        else:
            server_name = self.app.config.get('SERVER_NAME') or 'localhost'
            expected_location = urljoin(f'http://{server_name}', location)

        valid_status_codes = (301, 302, 303, 305, 307)
        valid_status_code_str = ', '.join(str(code) for code in valid_status_codes)
        not_redirect = f'HTTP Status {valid_status_code_str} expected but got {response.status_code:d}'
        self.assertTrue(response.status_code in valid_status_codes, message or not_redirect)
        self.assertEqual(response.location, expected_location, message)

    def assertStatus(self, response, status_code, message=None):
        '''
        Helper method to check matching response status.

        :param response: Flask response
        :param status_code: response status code (e.g. 200)
        :param message: Message to display on test failure
        '''

        message = message or f'HTTP Status {status_code} expected but got {response.status_code}'
        self.assertEqual(response.status_code, status_code, message)

    def assert200(self, response, message=None):
        '''
        Checks if response status code is 200

        :param response: Flask response
        :param message: Message to display on test failure
        '''

        self.assertStatus(response, 200, message)

    def assert400(self, response, message=None):
        '''
        Checks if response status code is 400

        :versionadded: 0.2.5
        :param response: Flask response
        :param message: Message to display on test failure
        '''

        self.assertStatus(response, 400, message)

    def assert401(self, response, message=None):
        '''
        Checks if response status code is 401

        :versionadded: 0.2.1
        :param response: Flask response
        :param message: Message to display on test failure
        '''

        self.assertStatus(response, 401, message)

    def assert403(self, response, message=None):
        '''
        Checks if response status code is 403

        :versionadded: 0.2
        :param response: Flask response
        :param message: Message to display on test failure
        '''

        self.assertStatus(response, 403, message)

    def assert404(self, response, message=None):
        '''
        Checks if response status code is 404

        :param response: Flask response
        :param message: Message to display on test failure
        '''

        self.assertStatus(response, 404, message)

    def assert405(self, response, message=None):
        '''
        Checks if response status code is 405

        :versionadded: 0.2
        :param response: Flask response
        :param message: Message to display on test failure
        '''

        self.assertStatus(response, 405, message)

    def assert500(self, response, message=None):

        self.assertStatus(response, 500, message)
