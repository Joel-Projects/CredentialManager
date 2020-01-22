
from server.models import User


def test_new_user(db):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, hashed_password, authenticated, and role fields are defined correctly
    """
    user = User(username='testUsername', password='pass')
    db.session.add(user)
    db.session.commit()
    assert user.username == 'testUsername'
    assert user.password == 'pass'
    assert user.is_authenticated

