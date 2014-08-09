import urllib2
import json
import keys

battletag = keys.battletag

baseURL = "http://us.battle.net/api/d3/"

def getProfileInfo(tag):
    reqURL = baseURL + "profile/" + tag + "/"
    print "Request: " + reqURL
    content = urllib2.urlopen(reqURL).read()
    data = json.loads(content)
    return data

def getHeroInfo(tag, heroid):
    reqURL = baseURL + "profile/" + tag + "/hero/" + str(heroid)
    print "Request: " + reqURL
    content = urllib2.urlopen(reqURL).read()
    data = json.loads(content)
    return data

def json_response(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

def eliteKills(tag):
    content = getProfileInfo(tag)
    total_kills_existing = 0
    most_hero  = ""
    most_kills = 0

    for hero in content['heroes']:
        stats = getHeroInfo(tag,hero['id'])
        try:
            total_kills_existing += stats['kills']['elites']
            if stats['kills']['elites'] > most_kills:
                    most_kills = stats['kills']['elites']
                    most_hero = stats['name']
        except KeyError:
            pass

    total_kills = content['kills']['elites']

    print total_kills
    print most_hero
    print most_kills

    data = {}
    data['value'] = total_kills
    data['segments'] = { most_hero: most_kills }

    return data


if __name__ == "__main__":
    kills = json_response(eliteKills(battletag))
    print kills
