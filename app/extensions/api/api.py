"""
Extended Api implementation with an application-specific helpers
----------------------------------------------------------------
"""
import six
from six import iteritems

from flask_restplus_patched import Api as BaseApi

from .namespace import Namespace


class Api(BaseApi):
    """
    Having app-specific handlers here.
    """

    def namespace(self, *args, **kwargs):
        # The only purpose of this method is to pass custom Namespace class
        _namespace = Namespace(*args, **kwargs)
        self.namespaces.append(_namespace)
        return _namespace

    # def add_namespace_(self, ns, path=None):
    #     '''
    #     This method registers resources from namespace for current instance of api.
    #     You can use argument path for definition custom prefix url for namespace.
    #
    #     :param Namespace ns: the namespace
    #     :param path: registration prefix of namespace
    #     '''
    #     if ns not in self.namespaces:
    #         self.namespaces.append(ns)
    #         if self not in ns.apis:
    #             ns.apis.append(self)
    #         # Associate ns with prefix-path
    #         if path is not None:
    #             self.ns_paths[ns] = path
    #     # Register resources
    #     for r in ns.resources:
    #         urls = self.ns_urls(ns, r.urls)
    #         self.register_resource(ns, r.resource, *urls, **r.kwargs)
    #     # Register models
    #     for name, definition in six.iteritems(ns.models):
    #         self.models[name] = definition
