import pytest

from app import extensions


@pytest.mark.parametrize(
    "extension_name",
    [
        "db",
        "login_manager",
        "marshmallow",
        "api",
        "cross_origin_resource_sharing",
        "logging",
        "bootstrap",
        "moment",
    ],
)
def test_extension_availability(extension_name):
    assert hasattr(extensions, extension_name)
