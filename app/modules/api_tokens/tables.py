from flask_login import current_user

from app.extensions.frontend.tables import (
    BaseCol,
    BaseTable,
    BoolIconColumn,
    CopyableField,
    DatetimeColumn,
    OwnerCol,
)


class ApiTokenTable(BaseTable):
    html_attrs = {"id": "api_tokens_table"}

    def __init__(self, items, *args, route_kwargs=None, **kwargs):
        if route_kwargs is None:
            route_kwargs = {"endpoint": "api_tokens.api_tokens"}
        self.route_kwargs = route_kwargs
        self.add_column("Name", BaseCol("Name", "name"))
        self.add_column("Token", CopyableField("Token", "token"))
        self.add_column("Enabled", BoolIconColumn("Enabled", "enabled"))
        self.add_column("Last Used", DatetimeColumn("Last Used", attr="last_used"))

        if current_user.is_admin or current_user.is_internal:  # pragma: no cover
            self.add_column("Owner", OwnerCol("Owner", attr_list=["owner", "username"]))

        super().__init__(items, *args, **kwargs)
