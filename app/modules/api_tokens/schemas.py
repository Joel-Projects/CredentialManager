from flask_restplus_patched import ModelSchema

from .models import ApiToken


class BaseApiTokenSchema(ModelSchema):
    '''
    Base API Token schema exposes only the most general fields.
    '''

    class Meta:
        model = ApiToken
        fields = (
            ApiToken.id.key,
            ApiToken.name.key
        )

class DetailedApiTokenSchema(BaseApiTokenSchema):
    '''
    Detailed API Token schema exposes all useful fields.
    '''

    class Meta(BaseApiTokenSchema.Meta):
        fields = BaseApiTokenSchema.Meta.fields + (
            ApiToken.token.key,
            ApiToken.owner_id.key,
            ApiToken.enabled.key
        )