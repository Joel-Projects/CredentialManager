def assert202Profile(response):
    assert response.status_code == 202
    assert response.mimetype == 'text/html'
    assert response.location == 'http://localhost/profile'