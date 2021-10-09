# pragma: no cover
import re
from datetime import datetime, timezone

import requests
from requests.auth import AuthBase


class SentryRequestorError(Exception):
    def __init__(self, error):
        self.error = error


class SentryResponse(object):
    def __init__(self, data: dict, name=None):
        self.__name__ = name
        regex = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3,6}Z")
        for key, value in data.items():
            if isinstance(value, dict):
                self.__setattr__(key, SentryResponse(value, key))
            elif isinstance(value, str):
                if regex.match(value):
                    self.__setattr__(
                        key,
                        datetime.fromisoformat(value.strip("Z")).replace(tzinfo=timezone.utc).astimezone(),
                    )
                else:
                    self.__setattr__(key, value)
            elif isinstance(value, list):
                self.__setattr__(
                    key,
                    [SentryResponse(i, key) if isinstance(i, dict) else i for i in value],
                )

    def __repr__(self):
        if self.__name__:
            return f"<{self.__name__}>"


class SentryAuthHeader(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request


class SentryRequestor(object):
    def __init__(self, token: str, endpoint="https://sentry.jesassn.org"):
        self.endpoint = endpoint
        self.token = token
        self.session = requests.Session()
        self.session.auth = SentryAuthHeader(self.token)

    def _request(self, method, url, item_name=None, params=None, data=None, json=None, raw=False):
        response = self.session.request(method, f"{self.endpoint}{url}", params=params, data=data, json=json)
        response_data = response.json()
        if "error" in response_data:
            raise SentryRequestorError(response_data["error"])
        if not raw:
            if isinstance(response_data, list):
                return [SentryResponse(item, item_name) for item in response_data]
            return SentryResponse(response_data, item_name)
        else:
            return response_data

    def get(self, url, item_name=None, params=None, raw=False):
        return self._request("GET", url, params=params, item_name=item_name, raw=raw)

    def post(self, url, item_name=None, data=None, json=None, raw=False, **kwargs):
        return self._request("POST", url, data=data, json=json, item_name=item_name, raw=raw, **kwargs)

    def put(self, url, item_name=None, data=None, json=None, raw=False, **kwargs):
        return self._request("PUT", url, data=data, json=json, item_name=item_name, raw=raw, **kwargs)

    def delete(self, url, params=None, raw=False):
        return self._request("DELETE", url, params=params, raw=raw)
