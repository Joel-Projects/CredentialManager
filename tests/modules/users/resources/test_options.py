import pytest

@pytest.mark.parametrize('path,status_code,expected_allowed_methods', (
    ('/api/v1/users/', 204, {'OPTIONS'}),
    ('/api/v1/users/1', 401, None),
))
def test_users_options_unauthorized(path, status_code, expected_allowed_methods, flask_app_client):
    response = flask_app_client.options(path)

    assert response.status_code == status_code
    if expected_allowed_methods:
        assert set(response.headers['Allow'].split(', ')) == expected_allowed_methods


@pytest.mark.parametrize('path,testUser,expected_allowed_methods', (
    ('/api/v1/users/{id}', None, {'OPTIONS'}),
    ('/api/v1/users/{id}', 'regular_user', {'OPTIONS', 'PATCH', 'GET'}),
    ('/api/v1/users/{id}', 'readonly_user', {'OPTIONS'}),
))
def test_users_options_authorized(path, testUser, expected_allowed_methods, flask_app_client, regular_user, readonly_user):
    userId = ''
    if testUser == 'regular_user':
        userId = regular_user.id
    elif testUser == 'readonly_user':
        userId = readonly_user.id
    with flask_app_client.login(regular_user):
        response = flask_app_client.options(path.format(id=userId))

    assert response.status_code == 204
    assert set(response.headers['Allow'].split(', ')) == expected_allowed_methods
