from app.extensions import InfoAttrs, StrName, Timestamp, db
from config import BaseConfig


class SentryToken(db.Model, Timestamp, InfoAttrs, StrName):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = "sentry_tokens"
    _display_name_plural = "Sentry Tokens"
    _name_attr = "app_name"
    _enabled_attr = "enabled"

    _info_attrs = {
        "id": "Sentry Token ID",
        "owner": "Owner",
        "bots_using_app": "Bots using this",
        "created": "Created at",
        "updated": "Last updated at",
    }

    __table_args__ = {"schema": BaseConfig.SCHEMA_NAME}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String)
    dsn = db.Column(db.String, nullable=False, info={"label": "DSN"})
    enabled = db.Column(db.Boolean, default=True, info={"label": "Enabled", "default": True})
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{BaseConfig.SCHEMA_NAME}.users.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = db.relationship("User", backref=db.backref(__tablename__, lazy="dynamic"))

    unique_constraint = db.UniqueConstraint(app_name, owner_id)

    def check_owner(self, user):
        if self.owner.is_internal:
            return user.is_internal
        return self.owner == user

    @property
    def bots_using_app(self):
        from app.modules.bots.models import Bot

        return Bot.query.filter_by(sentry_token=self).count()
