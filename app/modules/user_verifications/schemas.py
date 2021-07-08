from flask_marshmallow import base_fields

from flask_restplus_patched import ModelSchema

from .models import UserVerification


class BaseUserVerificationSchema(ModelSchema):
    """
    Base User Verification schema exposes only the most general fields.
    """

    class Meta:
        ordered = True
        model = UserVerification
        fields = (
            UserVerification.id.key,
            UserVerification.user_id.key,
            UserVerification.redditor.key,
            UserVerification.enabled.key,
            "resource_type",
        )
        dump_only = (UserVerification.id.key, "resource_type")
        load_only = (UserVerification.enabled.key,)

    _resource_type = Meta.model.__name__
    resource_type = base_fields.String(default=_resource_type)


class DetailedUserVerificationSchema(BaseUserVerificationSchema):
    """
    Detailed User Verification schema exposes all useful fields.
    """

    class Meta(BaseUserVerificationSchema.Meta):
        fields = BaseUserVerificationSchema.Meta.fields + (
            UserVerification.reddit_app_id.key,
            UserVerification.extra_data.key,
            UserVerification.owner_id.key,
        )
