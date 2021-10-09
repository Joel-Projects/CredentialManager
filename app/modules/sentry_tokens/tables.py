from flask_login import current_user

from app.extensions.frontend.tables import BaseCol, BaseTable, BoolIconColumn, DatetimeColumn, OwnerCol


class SentryTokenTable(BaseTable):
    html_attrs = {"id": "sentry_tokens_table"}

    def __init__(self, items, *args, route_kwargs=None, **kwargs):
        if route_kwargs is None:
            route_kwargs = {"endpoint": "sentry_tokens.sentry_tokens"}
        self.route_kwargs = route_kwargs
        self.add_column(
            "Name",
            BaseCol("Name", "app_name", td_html_attrs={"style": "text-align:left"}),
        )
        self.add_column("DSN", BaseCol("DSN", "dsn"))
        self.add_column("Created", DatetimeColumn("Created", attr="created"))
        self.add_column("Enabled", BoolIconColumn("Enabled", "enabled"))

        if current_user.is_admin or current_user.is_internal:
            self.add_column("Owner", OwnerCol("Owner", attr_list=["owner", "username"]))
        super().__init__(items, *args, **kwargs)
