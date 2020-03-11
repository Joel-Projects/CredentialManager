'''
Application Users management related tasks for Invoke.
'''

from getpass import getpass

from ._utils import app_context_task


@app_context_task
def create_user(
        context,
        username,
        is_internal=False,
        is_admin=False,
        is_regular_user=True,
        is_active=True
):
    '''
    Create a new user.
    '''
    from app.modules.users.models import User

    password = getpass('Enter password: ')

    new_user = User(
        username=username,
        password=password,
        is_internal=is_internal,
        is_admin=is_admin,
        is_regular_user=is_regular_user,
        is_active=is_active
    )

    from app.extensions import db
    with db.session.begin():
        db.session.add(new_user)