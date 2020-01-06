from PythonBots.BotModules.CommonUtils import getRemotePostgres, getReddit


sql = getRemotePostgres('personalBot')
sql.execute("SELECT * FROM compsubmissions WHERE comp='9ylvpx' ORDER BY ranking ASC")
results = sql.fetchall()
reddit = getReddit('personalBot')