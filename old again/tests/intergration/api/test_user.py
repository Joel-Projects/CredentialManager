import json, itertools
from server import User

def loginUser(client, data, key, user):
    if key:
        data['key'] = key
    else:
        client.post('/login', data=dict(username=user, password='password', csrf_token=client.csrf_token), content_type='application/x-www-form-urlencoded', follow_redirects=True)

def pytest_generate_tests(metafunc):
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )

def getDeleteResult(**kwargs):
    keys = {'admin': '12345', 'notadmin': '123457'}
    user, id, key = (kwargs.get(key) for key in ['user', 'id', 'key'])
    if user == 'notadmin':
        code = 403
        deleted = False
    else:
        if id == 3:
            code = 404
            deleted = False
        else:
            code = 200
            deleted = True
    if key:
        kwargs['key'] = keys[user]
    else:
        kwargs['key'] = None
    return {**kwargs, 'deleted': deleted, 'code': code}

class TestDeleteUser:

    users = [{'user': i} for i in ['admin', 'notadmin']]
    keys = {'admin': '12345', 'notadmin': '123457'}
    userIds = [{'id': i} for i in [1, 2, 3]]
    keyTests = [{'key': i} for i in [True, False]]
    results = []
    for i in itertools.product([{'model': User}], users, userIds, keyTests):
        kwargs = {key: value for item in i for key, value in item.items()}
        results.append(getDeleteResult(**kwargs))

    params = {
        'test_delete': results,
    }

    def test_delete(self, insertTestData, db, client, id, key, user, model, deleted, code):
        data = {'id': id}
        loginUser(client, data, key, user)
        oldItem = model.query.filter(model.id == id).first()
        response = client.delete('/api/user', data=data)
        assert response.status_code == code
        newItem = model.query.filter(model.id == id).first()
        if deleted:
            assert newItem is None
        else:
            assert oldItem == newItem


def getUpdateResult(**kwargs):
    keys = {'admin': '12345', 'notadmin': '123457'}
    user, id, key, newValues = (kwargs.get(key) for key in ['user', 'id', 'key', 'newValues'])
    if user == 'notadmin':
        code = 403
        updated = False
    else:
        if not any([i for i in newValues.values()]):
            code = 400
            updated = False
        else:
            if id == 3:
                code = 404
                updated = False
            else:
                code = 200
                updated = True
    if key:
        kwargs['key'] = keys[user]
    else:
        kwargs['key'] = None
    return {**kwargs, 'updated': updated, 'code': code}

class TestUpdateUser:

    users = [{'user': i} for i in ['admin', 'notadmin']]
    keys = {'admin': '12345', 'notadmin': '123457'}
    newValues = [
        {'newValues': {'wrongKey': None, 'username': None, 'password': None, 'admin': None}},
        {'newValues': {'wrongKey': None, 'username': 'newname', 'password': None, 'admin': None}},
        {'newValues': {'wrongKey': None, 'username': 'newname', 'password': 'newpass', 'admin': None}},
        {'newValues': {'wrongKey': None, 'username': 'newname', 'password': None, 'admin': False}},
        {'newValues': {'wrongKey': None, 'username': None, 'password': 'newpass', 'admin': None}},
        {'newValues': {'wrongKey': None, 'username': None, 'password': None, 'admin': False}},
        {'newValues': {'wrongKey': 'wrongKey', 'username': None, 'password': None, 'admin': None}}
    ]
    appId = [{'id': i} for i in [1, 2, 3]]
    keyTests = [{'key': i} for i in [True, False]]
    paramTests = []
    results = []
    for i in itertools.product(users, appId, keyTests, newValues):
        kwargs = {key: value for item in i for key, value in item.items()}
        results.append(getUpdateResult(**kwargs))

    params = {
        'test_update': results,
    }

    def test_update(self, insertTestData, db, client, id, key, user, updated, code, newValues, **kwargs):
        data = {'id': id, **kwargs}
        loginUser(client, data, key, user)
        oldItem = User.query.filter(User.id == id).first()
        attrs = {}
        username, password, admin, wrongKey = (newValues.get(key) for key in ['username', 'password', 'admin', 'wrongKey'])
        if username:
            attrs['username'] = username
        if password:
            attrs['password'] = password
        if admin:
            attrs['admin'] = admin
        if wrongKey:
            attrs['wrongKey'] = wrongKey
        data['attrs'] = json.dumps(attrs)
        response = client.patch('/api/user', data=data)
        assert response.status_code == code
        newItem = User.query.filter(User.id == id).first()
        if updated:
            if username:
                assert newItem.username == username
            if password:
                assert newItem.password == password
            if admin:
                assert newItem.admin == admin
        else:
            assert oldItem == newItem