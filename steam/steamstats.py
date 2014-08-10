import urllib2
import json
from operator import itemgetter
import inspect, os
import keys

#API key and userID
apiKey = keys.apiKey
userId = keys.userIdTQ

#URLs for API calls
baseURL = "http://api.steampowered.com/"
profileSummaryURL = "ISteamUser/GetPlayerSummaries/v0002/?"
recentlyPlayedURL = "IPlayerService/GetRecentlyPlayedGames/v0001/?"
ownedGamesURL = "IPlayerService/GetOwnedGames/v0001/?"
achievementsURL = "ISteamUserStats/GetPlayerAchievements/v0001/?"

FILE_LOCATION = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
OUTPUT_DIR = FILE_LOCATION + "/../output/"
outputFile = OUTPUT_DIR + "steam.json"

def getAppIds():
    content = urllib2.urlopen("http://api.steampowered.com/ISteamApps/GetAppList/v2").read()
    data = json.loads(content)
    return data

AppIdReference = getAppIds()

#Calculate string in days/hours/minutes from seconds number
def difference_dhm(seconds, max_units=2, use_smallcaps=True, use_words=False):
    if max_units < 1:
        raise ValueError('max_units must be >=1')
    divisors = ( 86400, 3600, 60, 1 )
    units = ( u'\u1d05', u'\u029c', u'\u1d0d', u'\uA731' ) if use_smallcaps else ( 'D', 'H', 'M', 'S' )
    units_singular = units
    if use_words:
        units = ( ' Days ', ' Hours ', ' Minutes ', ' Seconds')
        units_singular = ( ' Day ', ' Hour ', ' Minute ', ' Second')
    units_used = 0
    result = u"-" if seconds < 0 else u""
    remainder = abs(seconds)
    for d, u, s in zip(divisors, units, units_singular):
        if units_used >= max_units or (remainder == 0 and units_used > 0):
            break
        res, remainder = divmod(remainder, d)
        if res > 0 or d == 1:
            result += u"{}{}".format(int(res), u) if res > 1 else u"{}{}".format(int(res), s)
            units_used += 1
    return result

#Return API response for a user's owned games
#Includes appid of game and playtime forever + last2weeks
def getOwnedGames(key, user, appinfo=0, free_games=1):
    reqURL = baseURL + ownedGamesURL + "key=" + key + "&steamid=" + user
    reqURL += "&include_appinfo=" + str(appinfo) + "&include_played_free_games=" + str(free_games)
    print "Request: " + reqURL
    content = urllib2.urlopen(reqURL).read()
    data = json.loads(content)
    return data['response']

#Returns API response for a user's profile summary
def getProfileSummary(key, user):
    reqURL = baseURL + profileSummaryURL + "key=" + key + "&steamids=" + user
    print "Request: " + reqURL
    content = urllib2.urlopen(reqURL).read()
    data = json.loads(content)
    #this api call can return info on multiple players, using it for only one here
    return data['response']['players'][0] 

#Returns API response for a user's recently played games
def getRecentlyPlayed(key, user, count=0):
    reqURL = baseURL + recentlyPlayedURL + "key=" + key + "&steamid=" + user
    reqURL += "&count=" + str(count) if count else ''
    print "Request: " + reqURL
    content = urllib2.urlopen(reqURL).read()
    data = json.loads(content)
    return data['response']

#Return achievements for user for specific game by appid
def getAchievements(key, user, appid):
    reqURL = baseURL + achievementsURL + "key=" + key + "&steamid=" + user
    reqURL += "&appid="  + str(appid)
    print "Request: " + reqURL
    try:
        content = urllib2.urlopen(reqURL).read()
    except urllib2.HTTPError, err:
        if err.code == 400:
            return False
    data = json.loads(content)
    return data['playerstats']

def getTotalAchievements():
    content = getOwnedGames(apiKey, userId, appinfo=1)
    total_achievements = 0
    game_achvs = 0
    most_achvs = 0
    most_name = ""
    for game in content['games']:
        game_achvs = 0
        if game['playtime_forever'] > 0:
            achvs = getAchievements(apiKey, userId, game['appid'])
            if achvs:
                for achv in achvs['achievements']:
                    game_achvs += 1 if achv['achieved'] else 0
                total_achievements += game_achvs
                if game_achvs > most_achvs:
                    most_achvs = game_achvs
                    most_name = game['name']

    data = {}
    data['value'] = total_achievements
    data['segments'] = { most_name: most_achvs}

    return data

#Tile showing list of recently played games
#and playtime over the last 2 weeks
def recentlyPlayedTile():
    content = getRecentlyPlayed(apiKey, userId)
    total_mins = 0
    data = {
        'tileType': 'list',
    }
    data['data'] = {
           'cols': [
               {'label':'game', 'type': 'string' },
               {'label':'time', 'type': 'number' },
           ],
           'rows': [],
    }
    if content['total_count'] > 0:
        for game in content['games']:
            time_str = difference_dhm(game['playtime_2weeks'] * 60)
            data['data']['rows'].append([game['name'], time_str])
            total_mins += game['playtime_2weeks']

    time_str = difference_dhm(total_mins * 60)
    data['data']['rows'].append(['Total Playtime', time_str])

    data['value'] = time_str

    return data

#tile showing total playtime over lifetime of account
#Also shows playtime for most played game ever
def lifetimePlaytimeTile():
    content = getOwnedGames(apiKey, userId, appinfo=1)
    total_mins = 0
    sortedGames = sorted(content['games'], key=itemgetter('playtime_forever'), reverse=True)
    for game in sortedGames:
        total_mins+= game['playtime_forever']

    tot_str = difference_dhm(total_mins * 60, max_units=2, use_words=True)
    topGames = sortedGames[:10]
    listVals=[]
    for game in topGames:
        completed = 0
        incomplete = 0
        achvs = getAchievements(apiKey, userId, game['appid'])
        if achvs:
            for achv in achvs['achievements']:
                if achv['achieved'] == 1:
                    completed += 1
                else:
                    incomplete += 1
        info = {}
        info['name'] = game['name']
        info['playtime_min'] = game['playtime_forever']
        info['playtime_hours'] = int(game['playtime_forever']/60)
        info['playtime_str'] = difference_dhm(60 * game['playtime_forever'], use_words=True)
        info['achvComplete'] = completed
        info['achvIncomplete'] = incomplete
        info['icon_url'] = 'http://media.steampowered.com/steamcommunity/public/images/apps/' + str(game['appid']) + '/' + game['img_icon_url'] + '.jpg'
        info['game_page'] = 'http://store.steampowered.com/app/' + str(game['appid'])
        try:
            info['pct_complete'] = int(float(completed) / float((completed + incomplete)) * 100)
        except ZeroDivisionError:
            info['pct_complete'] = '?'
        listVals.append(info)

    data = {}
    data['value_str'] = tot_str
    data['value_min'] = total_mins
    data['listValues'] = listVals
    return data

#Returns name of game from appid
def getAppFromId(id):
    name = "undefined"
    for app in AppIdReference['applist']['apps']:
        if app['appid'] == id:
            name = app['name']
            return name
        elif app['appid'] > id:
            return name
    return name

def getProfileInfo():
    content = getProfileSummary(apiKey, userId)
    if 'timecreated' in content:
        print "PRIVATE INFO"
    else:
        print "PUBLIC INFO ONLY"
    data = {}
    data['username'] = content['personaname']
    return data

def json_response(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    playforever = lifetimePlaytimeTile()
    profile = getProfileInfo()
    steamStats = {}
    steamStats['playedForever'] = playforever
    steamStats['username'] = profile['username']
    file = open(outputFile, 'w')
    file.write(json_response(steamStats))
    file.close()
