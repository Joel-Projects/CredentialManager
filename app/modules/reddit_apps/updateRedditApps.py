from BotUtils.CommonUtils import BotServices
from bs4 import BeautifulSoup
import sys, psycopg2, os

services = BotServices('personalBot')
sql = services.postgres()
# perfsPageFile = sys.argv[1]
with open('/Users/jkpayne/Desktop/Bots/apps', 'r') as f:
    prefsPage = f.read()

apps = BeautifulSoup(prefsPage).find_all('div', class_='content')[0].find_all('div', id='developed-apps')[0]
developedApps = [i for i in BeautifulSoup(prefsPage).find_all('div', class_='content')[0].find_all('div', id='developed-apps')[0].children][1]
appsFinal = [(form.select('table')[0].findAll('input'), form.select('table')[0].findAll('tr')) for form in apps.findAll('form') if form.select('table')]
redditApps = {redditApp['name']: redditApp for redditApp in [{value['name']: value['value'] for value in app[0]} for app in appsFinal]}
perfapps = [[tr for tr in table.findAll('tr') ]for table in apps.findAll('table', class_='preftable')]
appsWithSecrets = [i for i in perfapps if 'developers' not in str(i) and 'secret' in str(i)]
secretAppNames = [row for app in appsWithSecrets for row in app if '"name"' in str(row)]
secretAppSecrets = [row for app in appsWithSecrets for row in app if 'secret' in str(row)]
for app in zip(secretAppNames, secretAppSecrets):
    app_name = app[0].find('td').find('input').attrs['value']
    redditApps[app_name]['client_secret'] = app[1].find('td').text
for app in developedApps:
    app_name = app.select('div.app-details > h2')[0].getText()
    appType = app.select('div.app-details > h3')[0].getText()
    client_id = app.select('div.app-details > h3')[1].getText()
    app = redditApps[app_name]
    app['app_name'] = app_name
    app['type'] = appType
    app['client_id'] = client_id

redditAppsFinal = {}
for app in redditApps:
    redditApp = redditApps[app]
    if not redditApp['about_url']:
        redditApp.pop('about_url')
    if 'client_secret' in redditApp:
        redditAppsFinal[app] = redditApp
new = {}
for redditApp in redditAppsFinal:
    app = redditApps[redditApp]
    app["app_name"] = appName = app["app_name"].replace(" ", "_")
    app['user_agent'] = f'python:com.jkpayne.redditapps/{appName} by /u/Lil_SpazJoekp'
    app['type'] = app['type'].replace(' ', '_')
    try:
        sql.execute('INSERT INTO oauth.reddit_apps(app_name, client_id, client_secret, user_agent, type, redirect_uri) VALUES (%(app_name)s, %(client_id)s, %(client_secret)s, %(user_agent)s, %(type)s, %(redirect_uri)s);', app)
        if app['app_name'].startswith('SiouxBot_Log_Thread'):
            app['sentry'] = 'SiouxBotLogStream'
            sql.execute('INSERT INTO oauth.bots(bot_name, reddit, sentry) VALUES (%(app_name)s, %(app_name)s, %(sentry)s) ON CONFLICT(bot_name) DO UPDATE SET reddit = EXCLUDED.reddit, sentry = EXCLUDED.sentry;', app)
        elif app['app_name'].startswith('Better'):
            app['sentry'] = '2Botter2Loop'
            sql.execute('INSERT INTO oauth.bots(bot_name, reddit, sentry) VALUES (%(app_name)s, %(app_name)s, %(sentry)s) ON CONFLICT(bot_name) DO UPDATE SET reddit = EXCLUDED.reddit, sentry = EXCLUDED.sentry;', app)
        new[app['app_name']] = app
        print(f'Added {app["app_name"]} Successfully!')
    except psycopg2.IntegrityError:
        pass

urls = []
linksToClick = []
for app in new:
    if app.startswith('Better'):
        client_id = new[app]['client_id']
        sql.execute('SELECT state FROM oauth.reddit_apps WHERE client_id=%s', (client_id,))
        result = sql.fetchone()
        state = result[0]
        url = f'https://www.reddit.com/api/v1/authorize?client_id={client_id}&duration=permanent&redirect_uri=https%3A%2F%2Foauth.lilspazjoekp.com%2Freddit_oauth&response_type=code&scope=creddits+modcontributors+modmail+modconfig+subscribe+structuredstyles+vote+wikiedit+mysubreddits+submit+modlog+modposts+modflair+save+modothers+read+privatemessages+report+identity+livemanage+account+modtraffic+wikiread+edit+modwiki+modself+history+flair&state={state}'
        urls.append((app, url))
        linksToClick.append(url)
urls.sort(key=lambda k: k[0])

with open('linksToClick.txt', 'w') as f:
    f.write('\n'.join(linksToClick))

print() 