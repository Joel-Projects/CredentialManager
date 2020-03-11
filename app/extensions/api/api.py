from flask_restplus_patched import Api as BaseApi

from .namespace import Namespace


class Api(BaseApi):

    def namespace(self, *args, **kwargs):
        # The only purpose of this method is to pass custom Namespace class
        _namespace = Namespace(*args, **kwargs)
        self.namespaces.append(_namespace)
        return _namespace