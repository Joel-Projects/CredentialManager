import flask_marshmallow
from apispec.ext.marshmallow.swagger import field2property, fields2jsonschema
from flask_restplus.model import Model as OriginalModel
from werkzeug import cached_property


class SchemaMixin(object):

    def __deepcopy__(self, memo):
        # XXX: Flask-RESTplus makes unnecessary data copying, while
        # marshmallow.Schema doesn't support deepcopyng.
        return self

class Schema(SchemaMixin, flask_marshmallow.Schema):
    pass

class ModelSchema(SchemaMixin, flask_marshmallow.sqla.ModelSchema):
    dateformat = '%m/%d/%Y %I:%M:%S %p %Z'

class DefaultHTTPErrorSchema(Schema):
    status = flask_marshmallow.base_fields.Integer()
    message = flask_marshmallow.base_fields.String()

    def __init__(self, http_code, **kwargs):
        super(DefaultHTTPErrorSchema, self).__init__(**kwargs)
        self.fields['status'].default = http_code

class Model(OriginalModel):

    def __init__(self, name, model, **kwargs):
        # XXX: Wrapping with __schema__ is not a very elegant solution.
        if not hasattr(model, '__schema__') and not (isinstance(model, list) and '__schema__' in model[0]):
            model = {'__schema__': model}
        super(Model, self).__init__(name, model, **kwargs)

    @cached_property
    def __schema__(self):
        schema = self['__schema__']
        if isinstance(schema, flask_marshmallow.Schema):
            return fields2jsonschema(schema.fields)
        elif isinstance(schema, flask_marshmallow.base_fields.FieldABC):  # pragma: no cover
            return field2property(schema)  # pragma: no cover
        raise NotImplementedError()  # pragma: no cover