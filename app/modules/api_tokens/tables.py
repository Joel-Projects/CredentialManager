from flask_table import Col

from app.extensions.frontend.tables import BaseTable, BoolIconColumn, DatetimeColumn, OwnerCol, CopyableField


class TokenTable(BaseTable):

    def __init__(self, items, current_user=None):
        self.add_column('Name', Col('Name', 'name'))
        self.add_column('Token', CopyableField('Token', 'token'))
        self.add_column('Enabled', BoolIconColumn('Enabled', 'enabled'))
        self.add_column('Last Used', DatetimeColumn('Last Used', attr='last_used', datetime_format='%m/%d/%Y %I:%M:%S %p %Z'))

        if current_user.is_admin or current_user.is_internal:
            self.add_column('Owner', OwnerCol('Owner', attr_list=['owner', 'username']))

        super().__init__(items)

    html_attrs = {'id': 'api_tokens'}
