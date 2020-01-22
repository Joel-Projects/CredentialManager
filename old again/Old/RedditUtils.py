import time, sys, psycopg2, praw, prawcore, base64, urllib, random, string, hashlib, logging
from flask import Flask, request, redirect, render_template
from BotUtils.CommonUtils import getRedditApps, BotServices
from discord import Webhook, RequestsWebhookAdapter

botName = 'flask'
sql = None

# import gspread, json
# from oauth2client.service_account import ServiceAccountCredentials

# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# with open('gauth.json') as jsonfile: gspreadKey = json.load(jsonfile)
# credentials = ServiceAccountCredentials.from_json_keyfile_dict(gspreadKey, scope)
# gc = gspread.authorize(credentials)
# filesheet = gc.open("r/fakehistoryporn Logo Competition (Responses)")
# worksheet = [wk for wk in filesheet.worksheets() if wk.title == 'Form Responses 2'][0]
# cells = worksheet.range(f'B2:B{worksheet.row_count}')
# voters = [cell.value for cell in cells if not cell.value == '']

# def hasVoted(ipHash): 
#     return ipHash in voters

app = Flask(__name__, template_folder='./templates')

def genRef():
    return ''.join(random.choice(string.digits + string.ascii_letters) for i in range(15))

def main():
     # DB Connection
    global sql
    global crypto
    global services
    global logger
    services = BotServices('flask')
    logger = services.logger()
    try:
        sql = services.postgres()
    except Exception as error:
        print(f'Error connecting to DB: {error}')
        log(f'Error connecting to DB: {error}')
        return
    if __name__ == '__main__':
            app.run(debug=True)

@app.route('/reddit_oauth')
def reddit_callback():
    global sql
    global crypto
    global services
    state = request.args.get('state', '')
    code = request.args.get('code')
    if state == '' or code == '':
        return 'Hello, please contact <a href="https://www.reddit.com/message/compose?to=Lil_SpazJoekp&amp;subject=Reddit%20Auth">u/Lil_SpazJoekp</a> for help.'
    try:
        encodedAuthor = None
        redditapps = getRedditApps()
        if len(state) == 128:
            encodedAuthor = state[64:]
            state = state[:64]
        if state in redditapps:
            redditConfig = redditapps[state]
            appType = redditConfig['type']
            client_id = redditConfig['client_id']
            client_secret = redditConfig['client_secret']
            redirect_uri = redditConfig['redirect_uri']
            user_agent = redditConfig['user_agent']
            appName = redditConfig['app_name']
            webhookUrl = 'https://discordapp.com/api/webhooks/638068060044918802/0jdPhgxwt-0IEVOfXyKj03xQC-xDFKJk8Dr4TcfKf3_nmsW9t3QzpRIOE4dmS5l2aMoL'
            crypto = services._BotServices__TokenCrypto(appName, sql)
            reddit = praw.Reddit(**redditConfig)
            if encodedAuthor:
                webhook = Webhook.from_url(webhookUrl, adapter=RequestsWebhookAdapter())
                state = encodedAuthor
                try:
                    token = reddit.auth.authorize(code)
                except prawcore.exceptions.OAuthException as error:
                    return handleError(error, appName)
                user = reddit.user.me(use_cache=False).name
                logger.info(f'user: {user}')
                sql.execute('SELECT * FROM verified WHERE encoded_id=%s', (state,))
                results = sql.fetchone()
                logger.info(f'results: {results}')
                newUser = True
                if results:
                    if results.redditor:
                        newUser = False
                    sql.execute('UPDATE verified SET redditor=%s WHERE encoded_id=%s',  (user, state))
                    if newUser:
                        webhook.send(f'.done {results.member_id}')
                    return render_template('success.html', user=user)
                else:
                    return render_template('help.html')
            else:
                # redirect_uri = 'http://localhost:5000/reddit_oauth'
                try:
                    token = reddit.auth.authorize(code)
                except prawcore.exceptions.OAuthException as error:
                    return handleError(error, appName)
                redditor = reddit.user.me(use_cache=False).name
                scopes = list(reddit.auth.scopes())
                issued = psycopg2.TimestampFromTicks(time.time())
                data = (base64.b64encode(crypto.encrypt(token)).decode(), redditor, client_id, scopes, appName, appType, issued)
                print(f'data: {data}')
                log(f'data: {data}')
                sql.execute("SELECT * FROM oauth.refreshtokens WHERE redditor=%s AND appname=%s AND NOT revoked", (redditor, appName))
                results = sql.fetchall()
                if results:
                    for result in results:
                        sql.execute('UPDATE oauth.refreshtokens SET refreshtoken = %s, scopes = %s, issued = %s WHERE redditor=%s AND appname=%s', (base64.b64encode(crypto.encrypt(token)).decode(), scopes, issued, redditor, appName))
                        sql.execute('INSERT INTO oauth.oldrefreshtokens(refreshtoken, redditor, clientid, scopes, appname, apptype, issued, revoked) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', result)
                else:
                    sql.execute('INSERT INTO oauth.refreshtokens(refreshtoken, redditor, clientid, scopes, appname, apptype, issued) VALUES (%s, %s, %s, %s, %s, %s, %s)', data)
                data = ()
                return render_template('success.html', user=redditor, app=appName)
        else:
            return 'Hello, please contact <a href="https://www.reddit.com/message/compose?to=Lil_SpazJoekp&amp;subject=Reddit%20Auth">u/Lil_SpazJoekp</a> for help.'
    except Exception as error:
        return handleError(error, appName)

def handleError(error, appName):
    ref = genRef()
    logger.exception(error)
    errorType = error.__class__.__name__
    log(f'{errorType}: {error}\nRef: {ref}')
    body = urllib.parse.quote_plus(f'This error, "{errorType}: {error}", occured while I was trying to authorize "{appName}".\nRef: {ref}')
    return render_template('error.html', error=error, errorType=errorType, errorBody=body)

@app.route('/logocomp')
def logocomp():
    # global sql
    # if sql.closed:
    #     try:
    #         sql = getPostgres('flask')
    #         print("database connected")
    #         log("database connected")
    #     except Exception as error:
    #         print(f'Error connecting to DB: {error}')
    #         log(f'Error connecting to DB: {error}')
    #         return 'An error has occured. Please try again later'
    # error = request.args.get('error', '')
    # if error: return "Error: " + error
    # ip = request.environ['HTTP_CF_CONNECTING_IP']
    # print(f'Possible voter from: {ip}')
    # log(f'Possible voter from: {ip}')
    # ipHash = hashlib.sha256(str(ip).encode('utf-8')).hexdigest()
    # if hasVoted(ipHash): return '<p>It looks like you have already voted! If this is an error contact <a href="https://www.reddit.com/message/compose?to=Lil_SpazJoekp&amp;subject=Subreddit%20Logo%20Voting%20Issue">u/Lil_SpazJoekp</a></p>'
    # data = (ipHash, time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime()))
    # print(data)
    # log(data)
    # sql.execute('SELECT * FROM logovoters2 WHERE id=%s', (ipHash,))
    # results = sql.fetchall()
    # if results:
    #     sql.execute('UPDATE logovoters2 SET timestamp=%s WHERE id=%s', (time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime()), ipHash))
    # else:
    #     sql.execute('INSERT INTO logovoters2(id, timestamp) VALUES(%s, %s)', data)
    # return redirect(f'https/://docs.google.com/forms/d/e/1FAIpQLScGEVM_VLYlXEg3t1ORhE6LlQ9QijMzXW4hzguG5ad-Xi8aFQ/viewform?entry.32363796={ipHash}')

    return '<p>Hello, the Logo Competition has ended.</p><p>Redirecting to r/FakeHistoryPorn after <span id="countdown">10</span> seconds...</p><p><script type="text/javascript">function countdown(){(seconds-=1)<0?window.location="https://www.reddit.com/r/fakehistoryporn":(document.getElementById("countdown").innerHTML=seconds,window.setTimeout("countdown()",1e3))}var seconds=10;countdown();</script></p><a href="javascript:window.open(\'\',\'_self\').close();">Click here to cancel redirect and close tab. </a>'

@app.route('/keepalive')
def keepalive():
    global sql
    sql.execute('SELECT * FROM logovoters')
    sql.fetchone()
    return '{status: 200}'

@app.route('/')
def root(): 
    host = request.environ['HTTP_HOST']
    if host == 'rfakehistoryporn.com' or host == 'www.rfakehistoryporn.com':
        return redirect('https://fakehistoryporn.reddit.com')
    elif host == 'drone.lilspazjoekp.com':
        return redirect('')
    else:
        return 'Hello, please contact <a href="https://www.reddit.com/message/compose?to=Lil_SpazJoekp&amp;subject=Reddit%20Auth">u/Lil_SpazJoekp</a> for info.'

@app.route('/reddit')
def reddit():
    return redirect('https://fakehistoryporn.reddit.com')

@app.route('/voterid')
def voterid():
    ip = request.environ['HTTP_CF_CONNECTING_IP']
    return hashlib.sha256(str(ip).encode('utf-8')).hexdigest()

@app.route('/contact')
def contact():
    return redirect('https://www.reddit.com/message/compose?to=r/fakehistoryporn')

@app.route('/moderators')
def moderators():
    return redirect('https://www.reddit.com/r/fakehistoryporn/about/moderators')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    log(request.values()[2]['payload']['repository']['name'])
    return 'good'

def log(logEntry):
    try:
        with open('RedditUtils.log', 'a') as f:
            f.write(f'{time.strftime("%B %d, %Y at %I:%M:%S %p %Z", time.localtime())}: {logEntry}\n')
    except Exception as error:
            print(error)

main()