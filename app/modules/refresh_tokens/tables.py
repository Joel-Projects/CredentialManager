from app.extensions.frontend.tables import DatetimeColumn, BaseCol, BaseTable, OwnerCol, BoolIconColumn


class RefreshTokenTable(BaseTable):

    def __init__(self, items, current_user=None):
        self.add_column('Redditor', BaseCol('Redditor', 'redditor'))
        self.add_column('Reddit App', BaseCol('Reddit App', 'reddit_app'))
        self.add_column('Issued', DatetimeColumn('Issued', attr='issued', datetime_format='%m/%d/%Y %I:%M:%S %p %Z'))
        self.add_column('Revoked', BoolIconColumn('Enabled', 'revoked'))

        if current_user.is_admin or current_user.is_internal:
            self.add_column('Owner', OwnerCol('Owner', attr_list=['owner', 'username']))
        super().__init__(items)

    html_attrs = {'id': 'refresh_tokens_table'}
    _formFields = [
        'app_name',
        'short_name',
        'app_description',
        'client_id',
        'client_secret',
        'user_agent',
        'app_type',
        'redirect_uri',
        'enabled',
        'owner'
    ]