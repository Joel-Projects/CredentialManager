from server import userSerializer, botSerializer, redditAppSerializer, refreshTokenSerializer, sentrySerializer, databaseSerializer, apiTokenSerializer
from .models import User, Bot, RedditApp, RefreshToken, Sentry, Database, ApiToken

items = {
    'user': {
        'model': User,
        'serializer': userSerializer,
        'name': 'username',
        'displayName': 'User'
    },
     'bot': {
         'model': Bot,
         'serializer': botSerializer,
         'name': 'bot_name',
         'displayName': 'Bot'
     },
     'reddit_app': {
         'model': RedditApp,
         'serializer': redditAppSerializer,
         'name': 'app_name',
         'displayName': 'Reddit App'
     },
     'refresh_token': {
         'model': RefreshToken,
         'serializer': refreshTokenSerializer,
         'name': 'app_name',
         'displayName': 'Refresh Token'
     },
     'sentry_token': {
         'model': Sentry,
         'serializer': sentrySerializer,
         'name': 'app_name',
         'displayName': 'Sentry'
     },
     'database_credential': {
         'model': Database,
         'serializer': databaseSerializer,
         'name': 'app_name',
         'displayName': 'Database Credentials'
     },
     'api_token': {
         'model': ApiToken,
         'serializer': apiTokenSerializer,
         'name': 'name',
         'displayName': 'Api Token'
     }
}
