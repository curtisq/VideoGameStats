#VideoGameStats

This project is scipts to pull in data from various game APIs (Steam, Blizzard Games, League of Legends, etc.) and combine and display this data. Things displayed may include total playtime, total achievements and many other things.

###Steam

The majority of work put into this project involved pulling in stats from [Steam's Web API](https://developer.valvesoftware.com/wiki/Steam_Web_API). You can find this all under steam steam/ folder. The steam/page/ folder is where you fill find the files required to display the website made to gather information on a user's top 10 steam games. Under steam/python/ are python scripts that can be used to generate a similar page with a Jinja2 template. Initial plans involved using python and Jinja2 but switched to JavaScript and thus the most up-to-date files will be in steam/page.

To test this yourself without downloading the repo the page is hosted [here](http://steam.curtisq.com). As of now only limited bug testing has been done. If you enter the URL for your steam profile the web app should pull in information about your total playtime and top 10 games of all time and display it.

If you choose to clone the repo and adjust the scripts yourself you will need to sign up for your own API key.

###Riot

These scripts use the Riot Web API to pull in stats about league of legends users and calculate a rough estimate of total playtime. Scripts only grab and manipulate the info to print to command line as of now.

###Blizzard

These scripts use the Diablo 3 api currently to pull in some information about elite kills for a user's battlenet account. Information is gathered and printed out to command line, nothing more as of yet.
