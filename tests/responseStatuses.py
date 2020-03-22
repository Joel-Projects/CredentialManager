from tests.utils import assertRenderedTemplate


def assert200(response):
    assert response.status_code == 200
    assert response.mimetype == 'text/html'

def assert400(response):
    assert response.status_code == 400
    assert response.mimetype == 'text/html'

def assert401(response):
    assert response.status_code == 401
    assert response.mimetype == 'application/json'
    assert response.json['status'] == 401
    assert response.json['message'] == 'The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn\'t understand how to supply the credentials required.'

def assert403(response, templates):
    assert response.status_code == 403
    assert response.mimetype == 'text/html'
    assertRenderedTemplate(templates, 'errors/403.html')

def assert404(response, templates):
    assert response.status_code == 404
    assert response.mimetype == 'text/html'
    assertRenderedTemplate(templates, 'errors/404.html')

def assert422(response):
    assert response.status_code == 422
    assert response.mimetype == 'application/json'

def assert201(response):
    assert response.status_code == 201
    assert response.mimetype == 'text/html'

def assert202(response):
    assert response.status_code == 202
    assert response.mimetype == 'text/html'