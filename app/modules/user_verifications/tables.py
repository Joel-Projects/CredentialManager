from flask_login import current_user

from app.extensions.frontend.tables import BaseCol, BaseTable, DatetimeColumn, OwnerCol


class UserVerificationTable(BaseTable):
    html_attrs = {"id": "user_verifications_table"}

    def __init__(self, items, *args, route_kwargs=None, **kwargs):
        if route_kwargs is None:
            route_kwargs = {"endpoint": "user_verifications.user_verifications"}
        self.route_kwargs = route_kwargs
        self.add_column(
            "Redditor",
            BaseCol("Redditor", "redditor", td_html_attrs={"style": "text-align:left"}),
        )
        self.add_column("User ID", BaseCol("User ID", "user_id"))
        self.add_column("Reddit App", BaseCol("Reddit App", "reddit_app"))
        self.add_column(
            "Verified At", DatetimeColumn("Verified At", attr="verified_at")
        )

        if current_user.is_admin or current_user.is_internal:
            self.add_column("Owner", OwnerCol("Owner", attr_list=["owner", "username"]))
        super().__init__(items, *args, **kwargs)
