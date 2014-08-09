import urllib2
import json
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

def getAppIds():
    content = urllib2.urlopen("http://api.steampowered.com/ISteamApps/GetAppList/v2").read()
    data = json.loads(content)
    return data

AppIdReference = getAppIds()

#Calculate string in days/hours/minutes from seconds number
def difference_dhm(seconds, max_units=2, use_smallcaps=True):
    if max_units < 1:
        raise ValueError('max_units must be >=1')
    divisors = ( 86400, 3600, 60, 1 )
    units = ( u'\u1d05', u'\u029c', u'\u1d0d', u'\uA731' ) if use_smallcaps else ( 'D', 'H', 'M', 'S' ) 
    units_used = 0
    result = u"-" if seconds < 0 else u""
    remainder = abs(seconds)
    for d, u in zip(divisors, units):
        if units_used >= max_units or (remainder == 0 and units_used > 0):
            break
        res, remainder = divmod(remainder, d)
        if res > 0 or d == 1:
            result += u"{}{}".format(int(res), u)
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
    most_played_mins = 0
    most_played_id = 0
    for game in content['games']:
        total_mins+= game['playtime_forever']
        if game['playtime_forever'] > most_played_mins:
            most_played_mins = game['playtime_forever']
            most_played_id = game['name']
    most_played_hours = float(most_played_mins)/60 if most_played_mins < 6000 else most_played_mins/60
    total_hours = float(total_mins) / 60 if total_mins < 6000 else total_mins/60
    mp_str = difference_dhm(most_played_mins * 60)
    tot_str = difference_dhm(total_mins * 60, max_units=2)
    data = {}
    data['value'] = tot_str
    data['segments'] = { most_played_id: mp_str }
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

def genTilespec():
    output = {
            'tilespec':[
                {'displayTitle': 'PLAYTIME', 'displaySubtitle': 'LAST 2 WEEKS', 'url': 'steamtiles/playtime2week.json', 'group':'Activity', 'visible':True },
                {'displayTitle': 'PLAYTIME', 'displaySubtitle': 'FOREVER', 'url': 'steamtiles/playtimeforever.json', 'group':'Activity', 'visible':True },
                {'displayTitle': 'ACHIEVEMENTS', 'displaySubtitle': 'ALL TIME', 'url': 'steamtiles/steamachvs.json', 'group':'Activity', 'visible':True },
                {'displayTitle': 'PLAYTIME', 'displaySubtitle': 'LEAGUE OF LEGENDS', 'url': 'steamtiles/playtimeleague.json', 'group':'Activity', 'visible':True },
                {'displayTitle': 'ElITE KILLS', 'displaySubtitle': 'DIABLO 3', 'url': 'steamtiles/d3elitekills.json', 'group':'Activity', 'visible':True },
             ],
    }
    return output

def genDatasource():
    output = {
            'results': 'OK',
            'directory': [
                { 'type': 'tilespec', 'name': 'Steam Tiles', 'url': 'tilespec/steamdash'},
            ]
    }
    return output

def getProfileInfo():
    content = getProfileSummary(apiKey, userId)
    if 'timecreated' in content:
        print "PRIVATE INFO"
    else:
        print "PUBLIC INFO ONLY"
    return 1

def json_response(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    getProfileInfo()

    #datasource and tilespec
    datasource = json_response(genDatasource())
    tilespec = json_response(genTilespec())

    #Tiledata
    playTile = json_response(recentlyPlayedTile())
    playforever = json_response(lifetimePlaytimeTile())
    achv = json_response(getTotalAchievements())

    print playTile
    print playforever
    print achv
