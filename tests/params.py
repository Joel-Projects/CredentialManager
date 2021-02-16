import pytest


users = [
    pytest.lazy_fixture("adminUserInstance"),
    pytest.lazy_fixture("internalUserInstance"),
    pytest.lazy_fixture("regularUserInstance"),
]
labels = ["as_admin_user", "as_internal_user", "as_regular_user"]
