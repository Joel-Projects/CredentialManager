from flask_login import current_user

from app.extensions.frontend.tables import (
    BaseCol,
    BaseTable,
    BoolIconColumn,
    DatetimeColumn,
    OwnerCol,
)


class RedditAppTable(BaseTable):
    _form_fields = [
        "app_name",
        "app_description",
        "client_id",
        "client_secret",
        "user_agent",
        "app_type",
        "redirect_uri",
        "enabled",
        "owner",
    ]
    html_attrs = {"id": "reddit_apps_table"}

    def __init__(self, items, *args, route_kwargs=None, **kwargs):
        if route_kwargs is None:
            route_kwargs = {"endpoint": "reddit_apps.reddit_apps"}
        self.route_kwargs = route_kwargs
        self.add_column(
            "Name",
            BaseCol("Name", "app_name", td_html_attrs={"style": "text-align:left"}),
        )
        self.add_column("Client ID", BaseCol("Client ID", "client_id"))
        self.add_column("App Type", BaseCol("App Type", "app_type"))
        self.add_column("Created", DatetimeColumn("Created", attr="created"))
        self.add_column("Enabled", BoolIconColumn("Enabled", "enabled"))

        if current_user.is_admin or current_user.is_internal:
            self.add_column("Owner", OwnerCol("Owner", attr_list=["owner", "username"]))
        super().__init__(items, *args, **kwargs)
