from app.extensions.frontend.tables import BaseCol, BaseTable, BoolIconColumn, DatetimeColumn, OwnerCol


class RefreshTokenTable(BaseTable):

    def __init__(self, items, current_user=None, showOld=False):
        self.add_column('Redditor', BaseCol('Redditor', 'redditor', td_html_attrs={'style': 'text-align:left'}))
        self.add_column('Reddit App', BaseCol('Reddit App', 'reddit_app'))
        self.add_column('Issued At', DatetimeColumn('Issued', attr='issued_at'))
        if showOld: # pragma: no cover
            self.add_column('Current', BoolIconColumn('Current', 'valid'))

        if current_user.is_admin or current_user.is_internal:
            self.add_column('Owner', OwnerCol('Owner', attr_list=['owner', 'username']))
        super().__init__(items, canBeDisabled=False, editable=False)

    html_attrs = {'id': 'refresh_tokens_table'}