from flask_login import current_user
from flask_table import Col, LinkCol

from app.extensions.frontend.tables import BaseTable, BoolIconColumn, CreatedBy, ObjectCountCol, OwnerCol

class UserTable(BaseTable):

    def __init__(self, items, *args, **kwargs):
        self.add_column('Username', OwnerCol('Name', 'username', td_html_attrs={'style':'text-align:left'}))
        self.add_column('Bots', ObjectCountCol('Bots', 'bots'))
        self.add_column('Reddit Apps', ObjectCountCol('Reddit Apps', 'reddit_apps'))
        self.add_column('Database Credentials', ObjectCountCol('Database Credentials', 'database_credentials'))
        self.add_column('Sentry Tokens', ObjectCountCol('Sentry Tokens', 'sentry_tokens'))
        self.add_column('API Tokens', ObjectCountCol('API Tokens', 'api_tokens'))
        self.add_column('Active', BoolIconColumn('Active', 'is_active'))
        self.add_column('Created By', CreatedBy('Created By', attr_list=['createdBy', 'username'], tooltip=lambda item: f"Created at: {item.updated.astimezone().strftime('%m/%d/%Y %I:%M:%S %p %Z')}"))

        self.add_column('Active', BoolIconColumn('Active', 'is_active'))
        self.add_column('Admin', BoolIconColumn('Admin', 'is_admin'))

        if current_user.is_internal or current_user.username == 'spaz':
            self.add_column('Internal', BoolIconColumn('Internal', 'is_internal'))

        super().__init__(items, *args, **kwargs)

    html_attrs = {'id': 'users_table'}
