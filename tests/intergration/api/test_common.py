import pytest, itertools
from server import items

def pytest_generate_tests(metafunc):
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )

def getToggleResult(**kwargs):
    keys = {'admin': '12345', 'notadmin': '123457'}
    item_type, user, id, toggle, key = (kwargs.get(key) for key in ['item_type', 'user', 'id', 'toggle', 'key'])
    result = True
    if user == 'notadmin':
        if id == 2 and item_type != 'user':
            code = 202
            accepted = True
        else:
            code = 403
            accepted = False
    else:
        code = 202
        accepted = True
    if key:
        kwargs['key'] = keys[user]
    else:
        kwargs['key'] = None

    if toggle is None:
        if accepted:
            result = False
    else:
        if accepted:
            result = toggle
    return {**kwargs, 'result': result, 'code': code}

class TestToggle:


    users = [{'user': i} for i in ['admin', 'notadmin']]
    keys = {'admin': '12345', 'notadmin': '123457'}
    appId = [{'id': i} for i in [1, 2]]
    keyTests = [{'key': i} for i in [True, False]]
    toggleTests = [{'toggle': i} for i in [True, False, None]]
    results = []
    for i in itertools.product([{'model': value['model'], 'item_type': key} for key, value in items.items() if hasattr(value['model'], 'enabled')], users, appId, keyTests, toggleTests):
        kwargs = {key: value for item in i for key, value in item.items()}
        results.append(getToggleResult(**kwargs))
    disableTests = []
    enableTests = []
    unspecifiedTests = []
    for result in results:
        if result['toggle'] is None:
            del result['toggle']
            unspecifiedTests.append(result)
        elif result['toggle']:
            del result['toggle']
            enableTests.append(result)
        else:
            del result['toggle']
            disableTests.append(result)

    params = {
        'test_disable': disableTests,
        'test_enable': enableTests,
        'test_unspecified': unspecifiedTests
    }

    def test_disable(self, insertTestData, db, client, item_type, id, key, user, model, result, code):
        data = {'item_type': item_type, 'id': id, 'enabled': False}
        loginUser(client, data, key, user)
        response = client.post('/api/toggle', data=data)
        assert response.status_code == code
        item = model.query.filter(model.id == id).first()
        assert item.enabled == result

    def test_enable(self, insertTestData, client, item_type, id, key, user, model, result, code):
        data = {'item_type': item_type, 'id': id, 'enabled': True}
        loginUser(client, data, key, user)
        response = client.post('/api/toggle', data=data)
        assert response.status_code == code
        item = model.query.filter(model.id == id).first()
        assert item.enabled == result

    def test_unspecified(self, insertTestData, client, item_type, id, key, user, model, result, code):
        data = {'item_type': item_type, 'id': id}
        loginUser(client, data, key, user)
        response = client.post('/api/toggle', data=data)
        assert response.status_code == code
        item = model.query.filter(model.id == id).first()
        assert item.enabled == result

def loginUser(client, data, key, user):
    if key:
        data['key'] = key
    else:
        client.post('/login', data=dict(username=user, password='password', csrf_token=client.csrf_token), content_type='application/x-www-form-urlencoded', follow_redirects=True)

def getDeleteResult(**kwargs):
    keys = {'admin': '12345', 'notadmin': '123457'}
    item_type, user, id, key = (kwargs.get(key) for key in ['item_type', 'user', 'id', 'key'])
    if user == 'notadmin':
        if id == 2 and item_type != 'user':
            code = 202
            accepted = True
        else:
            code = 403
            accepted = False
    else:
        code = 202
        accepted = True
    if key:
        kwargs['key'] = keys[user]
    else:
        kwargs['key'] = None
    return {**kwargs, 'deleted': accepted, 'code': code}

class TestDelete:

    users = [{'user': i} for i in ['admin', 'notadmin']]
    keys = {'admin': '12345', 'notadmin': '123457'}
    appId = [{'id': i} for i in [1, 2]]
    keyTests = [{'key': i} for i in [True, False]]
    results = []
    for i in itertools.product([{'model': value['model'], 'item_type': key} for key, value in items.items() if hasattr(value['model'], 'enabled')], users, appId, keyTests):
        kwargs = {key: value for item in i for key, value in item.items()}
        results.append(getDeleteResult(**kwargs))

    params = {
        'test_delete': results,
    }

    def test_delete(self, insertTestData, db, client, item_type, id, key, user, model, deleted, code):
        data = {'item_type': item_type, 'id': id}
        loginUser(client, data, key, user)
        oldItem = model.query.filter(model.id == id).first()
        response = client.post('/api/delete', data=data)
        assert response.status_code == code
        newItem = model.query.filter(model.id == id).first()
        if deleted:
            assert newItem is None
        else:
            assert oldItem == newItem


def getUpdateResult(**kwargs):
    keys = {'admin': '12345', 'notadmin': '123457'}
    item_type, user, id, key = (kwargs.get(key) for key in ['item_type', 'user', 'id', 'key'])
    if user == 'notadmin':
        if id == 2 and item_type != 'user':
            code = 202
            accepted = True
        else:
            code = 403
            accepted = False
    else:
        code = 202
        accepted = True
    if key:
        kwargs['key'] = keys[user]
    else:
        kwargs['key'] = None
    return {**kwargs, 'deleted': accepted, 'code': code}

class TestUpdate:

    users = [{'user': i} for i in ['admin', 'notadmin']]
    keys = {'admin': '12345', 'notadmin': '123457'}
    appId = [{'id': i} for i in [1, 2]]
    keyTests = [{'key': i} for i in [True, False]]
    paramTests = []
    results = []
    for i in itertools.product([{'model': value['model'], 'item_type': key} for key, value in items.items() if hasattr(value['model'], 'enabled')], users, appId, keyTests):
        kwargs = {key: value for item in i for key, value in item.items()}
        results.append(getDeleteResult(**kwargs))

    params = {
        'test_delete': results,
    }

    def test_update(self, insertTestData, db, client, item_type, id, key, user, model, deleted, code, **kwargs):
        data = {'item_type': item_type, 'id': id}
        loginUser(client, data, key, user)
        oldItem = model.query.filter(model.id == id).first()
        response = client.post('/api/delete', data=data)
        assert response.status_code == code
        newItem = model.query.filter(model.id == id).first()
        if deleted:
            assert newItem is None
        else:
            assert oldItem == newItem