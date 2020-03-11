from app.extensions.frontend.tables import AppNameCol, BaseCol, BaseTable, BoolIconColumn, DatetimeColumn, OwnerCol


class BotTable(BaseTable):

    def __init__(self, items, current_user=None):
        self.add_column('Name', BaseCol('Name', 'app_name', td_html_attrs={'style': 'text-align:left'}))
        self.add_column('Reddit App', AppNameCol('Reddit App', attr_list=['reddit_app', 'app_name']))
        self.add_column('Sentry Token', AppNameCol('Sentry Token', attr_list=['sentry_token', 'app_name']))
        self.add_column('Database Credentials', AppNameCol('Database Credential', attr_list=['database_credential', 'app_name']))
        self.add_column('Created', DatetimeColumn('Created', attr='created'))
        self.add_column('Enabled', BoolIconColumn('Enabled', 'enabled'))

        if current_user.is_admin or current_user.is_internal:
            self.add_column('Owner', OwnerCol('Owner', attr_list=['owner', 'username']))
        super().__init__(items)

    html_attrs = {'id': 'bots_table'}