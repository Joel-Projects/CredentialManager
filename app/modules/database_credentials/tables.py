from flask_login import current_user

from app.extensions.frontend.tables import BaseCol, BaseTable, BoolIconColumn, DatetimeColumn, OwnerCol


class DatabaseCredentialTable(BaseTable):
    _form_fields = [
        "app_name",
        "database_flavor",
        "database_host",
        "database_port",
        "database_username",
        "database_password",
        "database",
        "use_ssh",
        "ssh_host",
        "ssh_port",
        "ssh_username",
        "ssh_password",
        "use_ssh_key",
        "private_key",
        "private_key_passphrase",
        "enabled",
    ]
    html_attrs = {"id": "database_credentials_table"}

    def __init__(self, items, *args, route_kwargs=None, **kwargs):
        if route_kwargs is None:
            route_kwargs = {"endpoint": "database_credentials.database_credentials"}
        self.route_kwargs = route_kwargs
        self.add_column(
            "Name",
            BaseCol("Name", "app_name", td_html_attrs={"style": "text-align:left"}),
        )
        self.add_column("Flavor", BaseCol("Flavor", "database_flavor"))
        self.add_column("Database Host", BaseCol("Database Host", "database_host"))
        self.add_column("SSH Tunnel", BoolIconColumn("SSH Tunnel", "use_ssh"))
        self.add_column("Created", DatetimeColumn("Created", attr="created"))
        self.add_column("Enabled", BoolIconColumn("Enabled", "enabled"))

        if current_user.is_admin or current_user.is_internal:
            self.add_column("Owner", OwnerCol("Owner", attr_list=["owner", "username"]))
        super().__init__(items, *args, **kwargs)
