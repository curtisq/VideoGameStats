import urllib2
import json
import keys

#API key and User account ID
apiKey = keys.apiKey
userId = keys.userIdCQ

#URLs for API calls
baseURL = "https://na.api.pvp.net/api/lol/"
summonerStatsURL = "na/v1.3/stats/by-summoner/"

def getAppIds():
    content = urllib2.urlopen("http://api.steampowered.com/ISteamApps/GetAppList/v2").read()
    data = json.loads(content)
    return data


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

def getSummonerStats(key, user, season="SEASON4"):
    reqURL = baseURL + summonerStatsURL + user + "/summary?"
    reqURL += "season=" + season + "&api_key=" + key
    print "Request: " + reqURL
    content = urllib2.urlopen(reqURL).read()
    data = json.loads(content)
    return data['playerStatSummaries']

def getPlaytimeStats():
    content = getSummonerStats(apiKey, userId, season="SEASON4")
    total_wins = 0
    gameStats = []
    for gtype in content:
        stats = {}
        stats['type'] = "S4-" + str(gtype['playerStatSummaryType'])
        stats['wins'] = gtype['wins']
        stats['losses'] = gtype['losses'] if 'losses' in gtype else -1
        stats['avgTime'] = 30
        stats['queueTime'] = 3
        gameStats.append(stats)
    content = getSummonerStats(apiKey, userId, season="SEASON3")
    for gtype in content:
        stats = {}
        stats['type'] = "S3-" + str(gtype['playerStatSummaryType'])
        stats['wins'] = gtype['wins']
        stats['losses'] = gtype['losses'] if 'losses' in gtype else -1
        stats['avgTime'] = 30
        stats['queueTime'] = 3
        gameStats.append(stats)

    for stats in gameStats:
        if stats['losses'] == -1:
            if "CoopVsAI" in stats['type']: #bots
                stats['losses'] = int(stats['wins'] * .1)
                stats['avgTime'] = 24
            elif "CAP5x5" in stats['type']: #team builder
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 33
                stats['queueTime'] = 6
            elif "Aram" in stats['type']: #aram
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 27
            elif "NightmareBot" in stats['type']: #nightmare bots
                stats['losses'] = int(stats['wins'] * .4)
                stats['avgTime'] = 27
            elif "Odin" in stats['type']: #dominion
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 25
            elif "RankedSolo5x5" in stats['type']: #Solo/Duo Ranked 5s
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 35
                stats['queueTime'] = 5
            elif "RankedTeam3x3" in stats['type']: #Ranked teams 3v3
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 29
                stats['queueTime'] = 5
            elif "RankedTeam5x5" in stats['type']: #Ranked teams 5v5
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 35
                stats['queueTime'] = 5
            elif "SummonersRift6x6" in stats['type']: #6v6 special game mode
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 30
            elif "Unranked" in stats['type']: #normals 5v5
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 33
            elif "Unranked3x3" in stats['type']: #normals 3x3
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 30
            elif "URF" in stats['type']:
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 30
            elif "OneForAll" in stats['type']:
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 27
            else:
                stats['losses'] = int(stats['wins'] * 1)
                stats['avgTime'] = 27

    return gameStats

def genPlaytimeTile():
    gameStats = getPlaytimeStats()
    most_played_type = ""
    most_played_mins = 0
    most_games = 0
    total_time = 0
    for stats in gameStats:
        games = stats['wins'] + stats['losses']
        total_time += (games) * (stats['avgTime'] + stats['queueTime'])
        if games > most_games:
            most_games = games
            most_played_type = stats['type']
            most_played_mins = (games) * (stats['avgTime'] + stats['queueTime'])

    total_time_str = difference_dhm(60 * total_time)

    data = {}
    data['value'] = total_time_str
    data['segments'] = { most_played_type: difference_dhm(60 * most_played_mins) }
    return data

def json_response(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    playtime = json_response(genPlaytimeTile())
    print playtime
