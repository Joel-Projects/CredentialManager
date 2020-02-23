from flask_marshmallow import base_fields
from flask_restplus_patched import ModelSchema

from .models import RefreshToken


class BaseRefreshTokenSchema(ModelSchema):
    """
    Base Refresh Token schema exposes only the most general fields.
    """
    class Meta:
        model = RefreshToken
        fields = (
            RefreshToken.id.key,
            RefreshToken.reddit_app.key,
            RefreshToken.redditor.key,
            RefreshToken.refresh_token.key
        )

class DetailedRefreshTokenSchema(BaseRefreshTokenSchema):
    """
    Detailed Refresh Token schema exposes all useful fields.
    """
    class Meta(BaseRefreshTokenSchema.Meta):
        fields = BaseRefreshTokenSchema.Meta.fields + (
            RefreshToken.owner_id.key,
            RefreshToken.refresh_token.key,
            RefreshToken.scopes.key,
            RefreshToken.issued_at.key,
            RefreshToken.revoked.key,
            RefreshToken.revoked_at.key
        )