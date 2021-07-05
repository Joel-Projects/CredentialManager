from flask_login import current_user

from app.extensions.frontend.tables import (
    BaseCol,
    BaseTable,
    BoolIconColumn,
    DatetimeColumn,
    OwnerCol,
)


class RefreshTokenTable(BaseTable):
    html_attrs = {"id": "refresh_tokens_table"}

    def __init__(self, items, *args, route_kwargs=None, **kwargs):
        if route_kwargs is None:
            route_kwargs = {"endpoint": "refresh_tokens.refresh_tokens"}
        self.route_kwargs = route_kwargs
        self.add_column(
            "Redditor",
            BaseCol("Redditor", "redditor", td_html_attrs={"style": "text-align:left"}),
        )
        self.add_column("Reddit App", BaseCol("Reddit App", "reddit_app"))
        self.add_column("Issued At", DatetimeColumn("Issued", attr="issued_at"))
        showOld = kwargs.pop("showOld", False)
        if showOld:  # pragma: no cover
            self.add_column("Current", BoolIconColumn("Current", "valid"))
        else:
            self._cols.pop("Current", None)

        if current_user.is_admin or current_user.is_internal:
            self.add_column("Owner", OwnerCol("Owner", attr_list=["owner", "username"]))
        super().__init__(items, canBeDisabled=False, editable=False, *args, **kwargs)
