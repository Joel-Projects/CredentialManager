from marshmallow import Schema, fields

class BaseSchema(Schema):
    class Meta:
        dateformat = '%m/%d/%Y %I:%M:%S %p %Z'

class UserSerializer(BaseSchema):
    id = fields.Integer()
    username = fields.String()
    password = fields.String(load_only=True)
    admin = fields.Boolean()
    created = fields.DateTime()
    created_by = fields.String()
    updated = fields.DateTime()
    updated_by = fields.String()
    enabled = fields.Boolean()

class BotSerializer(BaseSchema):
    id = fields.Integer()
    bot_name = fields.String()
    reddit = fields.Integer()
    sentry = fields.Integer()
    owner = fields.Integer()
    created = fields.DateTime()
    last_updated = fields.DateTime()

class RedditAppSerializer(BaseSchema):
    id = fields.Integer()
    app_name = fields.String()
    short_name = fields.String()
    client_id = fields.String()
    client_secret = fields.String()
    user_agent = fields.String()
    app_type = fields.String()
    redirect_uri = fields.String()
    owner = fields.Integer()
    state = fields.String()
    created = fields.DateTime()

class RefreshTokenSerializer(BaseSchema):
    id = fields.Integer()
    redditor = fields.String()
    app_name = fields.String()
    app_id = fields.Integer()
    refresh_token = fields.String()
    scopes = fields.List(fields.String())
    issued = fields.DateTime()

class SentrySerializer(BaseSchema):
    id = fields.Integer()
    app_name = fields.String()
    dsn = fields.String()
    owner = fields.Integer()
    created = fields.DateTime()

class DatabaseSerializer(BaseSchema):
    id = fields.Integer()
    database_name = fields.String()
    database_flavor = fields.String()
    database_host = fields.String()
    database_port = fields.Integer()
    database_username = fields.String()
    database_password = fields.String()
    database = fields.String()
    ssh = fields.Boolean()
    ssh_host = fields.String()
    ssh_port = fields.Integer()
    ssh_username = fields.String()
    ssh_password = fields.String()
    private_key = fields.String()
    private_key_passphrase = fields.String()
    owner = fields.Integer()
    created = fields.DateTime()

class ApiTokenSerializer(BaseSchema):
    id = fields.Integer()
    name = fields.String()
    token = fields.String()
    owner = fields.Integer()
    created = fields.DateTime()