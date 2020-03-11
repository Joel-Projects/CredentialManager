from app.extensions.frontend.tables import BaseCol, BaseTable, BoolIconColumn, DatetimeColumn, OwnerCol


class SentryTokenTable(BaseTable):

    def __init__(self, items, current_user=None):
        self.add_column('Name', BaseCol('Name', 'app_name', td_html_attrs={'style': 'text-align:left'}))
        self.add_column('DSN', BaseCol('DSN', 'dsn'))
        self.add_column('Created', DatetimeColumn('Created', attr='created'))
        self.add_column('Enabled', BoolIconColumn('Enabled', 'enabled'))

        if current_user.is_admin or current_user.is_internal:
            self.add_column('Owner', OwnerCol('Owner', attr_list=['owner', 'username']))
        super().__init__(items)

    html_attrs = {'id': 'sentry_tokens_table'}