import json

def genDict():
    with open ("./output/steam.json") as file:
        content = file.read()
    data = json.loads(content)
    hours = data['playedForever']['value_min'] / 60
    header = "You Have " + str(hours) + " Hours Played on Steam"
    topGames = data['playedForever']['listValues']
    topGames1to5 = topGames[:5]
    topGames6to10 = topGames[-5:]
    timestr = ""
    fdata = {}
    fdata['header_text'] = header
    fdata['username'] = data['username']
    fdata['time_str'] = data['playedForever']['value_str']
    fdata['topGames'] = topGames
    fdata['topGames1'] = topGames1to5
    fdata['topGames2'] = topGames6to10
    return fdata

values = genDict()
