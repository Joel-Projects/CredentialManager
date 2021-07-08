import pytest

users = [
    pytest.lazy_fixture("admin_user_instance"),
    pytest.lazy_fixture("internal_user_instance"),
    pytest.lazy_fixture("regular_user_instance"),
]
labels = ["as_admin_user", "as_internal_user", "as_regular_user"]
