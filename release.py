import requests, sys


SENTRY_API_TOKEN = sys.argv[1]
commit = sys.argv[2]
repoName = sys.argv[3]
author = sys.argv[4]
email = sys.argv[5]
message = sys.argv[6]

data = {'commits': [{'id': commit, 'repository': repoName, 'author_name': author, 'author_email': email, 'message': message}], 'version': commit, 'projects': [repoName]}
res = requests.post('https://sentry.jesassn.org/api/0/organizations/jes/releases/', json=data, headers={'Authorization': f'Bearer {SENTRY_API_TOKEN}'})