from flask_table import Col, LinkCol

from app.extensions.frontend.tables import BaseTable, BoolIconColumn, CopyableField, DatetimeColumn, OwnerCol


class ApiTokenTable(BaseTable):

    def __init__(self, items, current_user=None, user=None):
        if user:
            self.add_column('Name', LinkCol('Name', 'users.editItemsPerUser', 'name', url_kwargs={'user': user, 'item': '__tablename__', 'item_id': 'id'}))
        else:
            self.add_column('Name', Col('Name', 'name'))
        self.add_column('Token', CopyableField('Token', 'token'))
        self.add_column('Enabled', BoolIconColumn('Enabled', 'enabled'))
        self.add_column('Last Used', DatetimeColumn('Last Used', attr='last_used'))

        if current_user.is_admin or current_user.is_internal:
            self.add_column('Owner', OwnerCol('Owner', attr_list=['owner', 'username']))

        super().__init__(items)

    html_attrs = {'id': 'api_tokens_table'}