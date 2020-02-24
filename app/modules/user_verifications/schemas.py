from flask_marshmallow import base_fields
from flask_restplus_patched import ModelSchema

from .models import UserVerification


class BaseUserVerificationSchema(ModelSchema):
    """
    Base User Verification schema exposes only the most general fields.
    """
    class Meta:
        model = UserVerification
        fields = (
            UserVerification.id.key,
            UserVerification.reddit_app_id.key,
            UserVerification.discord_id.key,
            UserVerification.redditor.key
        )

class DetailedUserVerificationSchema(BaseUserVerificationSchema):
    """
    Detailed User Verification schema exposes all useful fields.
    """
    class Meta(BaseUserVerificationSchema.Meta):
        fields = BaseUserVerificationSchema.Meta.fields + (
            UserVerification.extra_data.key,
            UserVerification.owner_id.key
        )