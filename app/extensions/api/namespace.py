import logging
from contextlib import contextmanager
from functools import wraps

import flask_marshmallow
import sqlalchemy
from flask_restplus._http import HTTPStatus

from flask_restplus_patched.namespace import Namespace as BaseNamespace

from . import http_exceptions
from .webargs_parser import CustomWebargsParser

log = logging.getLogger(__name__)


class Namespace(BaseNamespace):

    WEBARGS_PARSER = CustomWebargsParser()

    def resolve_object_to_model(self, model, object_arg_name, identity_arg_names=None):
        """
        A helper decorator to resolve DB record instance by id.

        Arguments:
            model (type) - a Flask-SQLAlchemy model class with
                ``query.get_or_404`` method
            object_arg_name (str) - argument name for a resolved object
            identity_arg_names (tuple) - a list of argument names holding an
                object identity, by default it will be auto-generated as
                ``%(object_arg_name)s_id``.

        @namespace.resolve_object_to_model(User, 'user')
        def get_user_by_id(user):
            return user
        get_user_by_id(user_id=3)
        <User(id=3, ...)>

        @namespace.resolve_object_to_model(MyModel, 'my_model', ('user_id', 'model_name'))
        def get_object_by_two_primary_keys(my_model):
            return my_model
        get_object_by_two_primary_keys(user_id=3, model_name='test')
        <MyModel(user_id=3, name='test', ...)>
        """
        by_id = False
        if identity_arg_names is None:
            identity_arg_names = (f"{object_arg_name}_id",)
            by_id = True
        elif not isinstance(identity_arg_names, (list, tuple)):  # pragma: no cover
            identity_arg_names = (identity_arg_names,)
        if by_id:
            return self.resolve_object(
                object_arg_name,
                resolver=lambda kwargs: model.query.get_or_404(
                    [kwargs.pop(identity_arg_name) for identity_arg_name in identity_arg_names]
                ),
            )
        else:
            return self.resolve_object_args(
                object_arg_name,
                resolver=lambda kwargs: model.query.filter_by(
                    **{identity_arg_name: kwargs.pop(identity_arg_name) for identity_arg_name in identity_arg_names}
                ).first_or_404(),
            )

    def model(self, name=None, model=None, **kwargs):

        """
        A decorator which registers a model (aka schema / definition).

        This extended implementation auto-generates a name for
        ``Flask-Marshmallow.Schema``-based instances by using a class name
        with stripped off `Schema` prefix.
        """
        if isinstance(model, flask_marshmallow.Schema) and not name:
            name = model.__class__.__name__
            if name.endswith("Schema"):
                name = name[: -len("Schema")]
        # if name.startswith('HTTP'):
        #     return
        return super(Namespace, self).model(name=name, model=model, **kwargs)

    def login_required(self, locations=("headers",), allowed_auth_methods=["api_token", "basic"]):
        def decorator(func_or_class):

            if isinstance(func_or_class, type):
                func_or_class._apply_decorator_to_methods(decorator)
                return func_or_class
            func = func_or_class

            from app.modules.users import permissions

            if getattr(func, "_role_permission_applied", False):
                protected_func = func
            else:
                protected_func = self.permission_required(permissions.ActiveUserRolePermission())(func)

            return self.doc(security=allowed_auth_methods)(
                self.response(
                    code=HTTPStatus.UNAUTHORIZED.value,
                    description="Authentication is required",
                )
            )(protected_func)

        return decorator

    def restrict_enabled(self, object_from_kwargs):
        """
        A decorator which restricts getting objects that are disabled.

        This decorator puts together permissions restriction code with OpenAPI
        Specification documentation.

        Arguments:
            permission (Permission) - it can be a class or an instance of
                :class:``Permission``, which will be applied to a decorated
                function, and docstrings of which will be used in OpenAPI
                Specification.
            kwargs_on_request (func) - a function which should accept only one
                ``dict`` argument (all kwargs passed to the function), and
                must return an ``object``.
        """

        def decorator(func):
            def _disabled_check(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    in_args = False
                    if not kwargs:
                        in_args = True
                    if in_args:
                        enabled = object_from_kwargs(args[1]).enabled
                        args = (args[0], object_from_kwargs(args[1]))
                    else:
                        enabled = object_from_kwargs(kwargs).enabled
                    if not enabled:
                        http_exceptions.abort(
                            code=HTTPStatus.FAILED_DEPENDENCY,
                            message="Requested object is disabled",
                        )
                    return func(*args, **kwargs)

                return wrapper

            protected_func = _disabled_check(func)
            self._register_access_restriction_decorator(protected_func, _disabled_check)

            return self.doc(description=f"**Must be enabled**\n\n")(
                self.response(
                    code=HTTPStatus.FAILED_DEPENDENCY.value,
                    description="Requested object is disabled",
                )(protected_func)
            )

        return decorator

    def permission_required(self, permission, kwargs_on_request=None):
        """
        A decorator which restricts access for users with a specific
        permissions only.

        This decorator puts together permissions restriction code with OpenAPI
        Specification documentation.

        Arguments:
            permission (Permission) - it can be a class or an instance of
                :class:``Permission``, which will be applied to a decorated
                function, and docstrings of which will be used in OpenAPI
                Specification.
            kwargs_on_request (func) - a function which should accept only one
                ``dict`` argument (all kwargs passed to the function), and
                must return a ``dict`` of arguments which will be passed to
                the ``permission`` object.

        Example:
        >>> @Namespace.permission_required(
        ...     OwnerRolePermission,
        ...     kwargs_on_request=lambda kwargs: {'obj': kwargs['team']}
        ... )
        ... def get_team(team):
        ...     # This line will be reached only if OwnerRolePermission check
        ...     # is passed!
        ...     return team
        """

        def decorator(func):
            """
            A helper wrapper.
            """
            # Avoid circilar dependency
            from app.modules.users import permissions

            if getattr(permission, "_partial", False):  # pragma: no cover
                # We don't apply partial permissions, we only use them for
                # documentation purposes.
                protected_func = func
            else:
                if not kwargs_on_request:
                    _permission_decorator = permission
                else:

                    def _permission_decorator(func):
                        @wraps(func)
                        def wrapper(*args, **kwargs):
                            with permission(**kwargs_on_request(kwargs)):
                                return func(*args, **kwargs)

                        return wrapper

                protected_func = _permission_decorator(func)
                self._register_access_restriction_decorator(protected_func, _permission_decorator)
            if isinstance(permission, permissions.RolePermission) or (
                isinstance(permission, type) and issubclass(permission, permissions.RolePermission)
            ):
                protected_func._role_permission_applied = True

            permission_description = permission.__doc__.strip()
            return self.doc(description=f"**PERMISSIONS: {permission_description}**\n\n")(
                self.response(code=HTTPStatus.FORBIDDEN.value, description=permission_description)(protected_func)
            )

        return decorator

    def _register_access_restriction_decorator(self, func, decorator_to_register):
        """
        Helper function to register decorator to function to perform checks
        in options method
        """
        if not hasattr(func, "_access_restriction_decorators"):
            func._access_restriction_decorators = []
        func._access_restriction_decorators.append(decorator_to_register)

    def paginate(self, parameters=None, locations=None):
        """
        Endpoint parameters registration decorator special for pagination.
        If ``parameters`` is not provided default PaginationParameters will be
        used.

        Also, any custom Parameters can be used, but it needs to have ``limit`` and ``offset``
        fields.
        """
        if not parameters:
            # Use default parameters if None specified
            from app.extensions.api.parameters import PaginationParameters

            parameters = PaginationParameters()

        if not all(mandatory in parameters.declared_fields for mandatory in ("limit", "offset")):  # pragma: no cover
            raise AttributeError("`limit` and `offset` fields must be in Parameter passed to `paginate()`")

        def decorator(func):
            @wraps(func)
            def wrapper(self_, parameters_args, *args, **kwargs):
                queryset = func(self_, parameters_args, *args, **kwargs)
                total_count = queryset.count()
                return (
                    queryset.offset(parameters_args["offset"]).limit(parameters_args["limit"]),
                    HTTPStatus.OK,
                    {"X-Total-Count": total_count},
                )

            return self.parameters(parameters, locations)(wrapper)

        return decorator

    @contextmanager
    def commit_or_abort(
        self,
        session,
        default_error_message="The operation failed to complete",
        **kwargs,
    ):

        try:
            with session.begin():
                yield
        except ValueError as exception:  # pragma: no cover
            log.info(f"Database transaction was rolled back due to: {exception!r}")
            http_exceptions.abort(code=HTTPStatus.CONFLICT, message=str(exception), **kwargs)
        except sqlalchemy.exc.IntegrityError as exception:
            log.info(f"Database transaction was rolled back due to: {exception!r}")
            keys, values = tuple(
                map(
                    lambda item: item.split(", "),
                    exception.orig.args[0].splitlines()[1][14:-17].split(")=("),
                )
            )
            kwargs["error"] = "already exists"
            kwargs["items"] = {key: value for key, value in zip(keys, values)}
            http_exceptions.abort(code=HTTPStatus.CONFLICT, message=default_error_message, **kwargs)
