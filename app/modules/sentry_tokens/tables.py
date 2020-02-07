from flask_table import Table, LinkCol

from app.extensions.frontend.tables import DatetimeColumn, BaseCol, BaseTable


class SentryTokenTable(BaseTable):

    def __init__(self, items, current_user=None):
        self.add_column('Name', BaseCol('Name', 'name'))
        self.add_column('DSN', BaseCol('DSN', 'dsn'))
        self.add_column('Created', DatetimeColumn('Created', attr='created', datetime_format='%m/%d/%Y %I:%M:%S %p %Z'))

        if current_user.is_admin or current_user.is_internal:
            self.add_column('Owner', LinkCol('Owner', 'users.users', attr_list=['owner', 'username']))
        super().__init__(items)

    html_attrs = {'id': 'sentry_tokens_table'}