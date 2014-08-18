def genDict():
    with open ("./output/steam.json") as file:
        content = file.read()
    data = json.loads(content)
    hours = data['playedForever']['value_mins'] / 60
    header = "You Have" + str(hours) + "Hours Played on Steam"
    fdata['header_text'] = header
    fdata['username'] = data['username']
    fdata['time_str'] = data['playedForever']['value_str']
    return fdata

values = genDict()
