from app.extensions.frontend.tables import BaseCol, BaseTable, DatetimeColumn, OwnerCol


class UserVerificationTable(BaseTable):

    def __init__(self, items, current_user=None):
        self.add_column('Redditor', BaseCol('Redditor', 'redditor', td_html_attrs={'style': 'text-align:left'}))
        self.add_column('Discord Member ID', BaseCol('Discord Member ID', 'discord_id'))
        self.add_column('Reddit App', BaseCol('Reddit App', 'reddit_app'))
        self.add_column('Verified At', DatetimeColumn('Verified At', attr='verified_at'))

        if current_user.is_admin or current_user.is_internal:
            self.add_column('Owner', OwnerCol('Owner', attr_list=['owner', 'username']))
        super().__init__(items)

    html_attrs = {'id': 'user_verifications_table'}