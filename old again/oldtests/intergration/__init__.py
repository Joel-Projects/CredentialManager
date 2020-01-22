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
         'name': 'app_name',
         'displayName': 'Api Token'
     }
}