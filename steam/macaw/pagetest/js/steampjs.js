/*steamjson.js
 *This file contains the functions needed for getting information from the Steam API
 *This will be used by the steam playtime VGstats test by Curtis and Ryan Quintal
 */
var baseURL = "http://api.steampowered.com/";
var profileSummaryURL = "ISteamUser/GetPlayerSummaries/v0002/?";
var ownedGamesURL = "IPlayerService/GetOwnedGames/v0001/?";
var achievementsURL = "ISteamUserStats/GetPlayerAchievements/v0001/?";
var recentlyPlayedURL = "IPlayerService/GetRecentlyPlayedGames/v0001/?";


function getJson(url) {
	console.log("Requesting JSON from URL " + url);
	$.getJSON( url, function( data ) {
		var items = [];
		$.each( data, function( key, val ) {
			items.push( "<li id='" + key + "'>" + val + "</li>" );
		});
		     
		$( "<ul/>", {
			"class": "my-new-list",
			html: items.join( "" )
		}).appendTo( "body" );
	});
	console.log("Request Finished");
}

/* Takes api key and steam id
 * returns object with user's steam profile info
 */
function getProfileSummary(apiKey, userId) {

	var url = baseURL + profileSummaryURL + "&steamids=" + userId;
	console.log("Requesting: " + url);
	var mydata = {};
	$.ajax({
		url: "./proxy.php",
		async: false,
		dataType: 'json',
		data: { requrl: url },
		success: function (json) {
			mydata = json["response"]["players"][0];
		}
	});
	console.log("Request finished");
	return mydata;
}

/* Takes api key and steam id
 * returns object with user's owned game list
 */
function getOwnedGames(apiKey, userId) {

	var url = baseURL + ownedGamesURL + "&steamid=" + userId;
	url += "&include_appinfo=1" + "&include_played_free_games=1";
	console.log("Requesting: " + url);
	var mydata = {};
	$.ajax({
		url: "./proxy.php",
		async: false,
		dataType: 'json',
		data: { requrl: url },
		success: function (json) {
			mydata = json["response"];
		}
	});
	console.log("Request finished");
	return mydata;
}

/* Takes api key and steam id
 * returns object with user's owned game list
 */
function getGameAchievements(apiKey, userId, appid) {

	var url = baseURL + achievementsURL + "&steamid=" + userId;
	url += "&appid=" + appid;
	console.log("Requesting: " + url);
	var mydata = {};
	$.ajax({
		url: "./proxy.php",
		async: false,
		dataType: 'json',
		data: { requrl: url },
		success: function (json) {
			mydata = json["playerstats"];
		}
	});
	console.log("Request finished");
	return mydata;
}

function compare_playtime(a,b) {
	if(a['playtime_forever'] < b['playtime_forever'])
		return -1;
	if(a['playtime_forever'] > b['playtime_forever'])
		return 1;
	return 0;
}

function playtimeTotal(key, id) {
	var data = getOwnedGames(key, id);
	var games = data['games'];
	var sorted_games = games.sort(compare_playtime);
	sorted_games.reverse(); //high to low
	var top_games = sorted_games.slice(0,10)
	var total_mins = 0;
	for (var game in sorted_games) {
		total_mins += sorted_games[game]['playtime_forever'];
	}
	listVals = [];
	for (var game in top_games) {
		var total_achvs = 0;
		var comp_achvs = 0;
		var info = {}
		info['playtime_mins'] = top_games[game]['playtime_forever'];
		info['playtime_hours'] = Math.round(top_games[game]['playtime_forever']/60);
		info['name'] = top_games[game]['name'];
		info['rank'] = parseInt(game) + 1;
		info['icon_url'] = 'http://media.steampowered.com/steamcommunity/public/images/apps/' + top_games[game]['appid'] + '/' + top_games[game]['img_icon_url'] + '.jpg';
		info['game_page'] = 'http://store.steampowered.com/app/' + top_games[game]['appid'];
		achievs = getGameAchievements(key, id, top_games[game]['appid']);
		for (achv in achievs['achievements']) {
			total_achvs++;
			if (achievs['achievements'][achv]['achieved'] == 1) {
				comp_achvs++;
			}	
		}
		info['total_achvs'] = total_achvs;
		info['comp_acvs'] = comp_achvs;
		info['pct_complete'] = Math.round((comp_achvs / total_achvs) * 100);
		listVals.push(info)
	}
	
	var allinfo = {}
	allinfo['total_playtime_min'] = total_mins;
	allinfo['total_playtime_hours'] = Math.round(total_mins / 60);
	allinfo['top10'] = listVals;
	console.log(allinfo)
	return allinfo
}

/*Get url params
 * from stackoverflor
 */
function getParameterByName(name) {
	name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
	    results = regex.exec(location.search);
	return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

/*Test out API json fetching functions
 */
function test() {
	console.log("start all");
	var newid = getParameterByName('steamid');
	if (newid != null) id = newid;

	key = "";

	//get profile info
	var profileinfo = getProfileSummary(key, id);
	console.log(profileinfo);
	//get playtime info
	var playinfo = playtimeTotal(key, id);
	console.log(playinfo);

	var top5 = playinfo['top10'].slice(0,5);
	var bot5 = playinfo['top10'].slice(5,10);
	//Replace headline text
	$('#main-headline').text("You've played " + playinfo['total_playtime_hours'] + " hours of games.");
	$('#subhead').text("That's " + playinfo['total_playtime_hours'] + " hours of games, " + profileinfo['personaname'] + ".");
	//Generate Game lists
	for (game in top5){
		var p = "<p>" + top5[game]['rank'] + ". " + top5[game]['name'] + "<br><span>Played " + top5[game]['playtime_hours'] + " hrs.";
		p += top5[game]['pct_complete'] + "% Completed.</span></p>";
		$('._text-5').append(p);
	}
	//generate image icons
	for (game in top5){
		var d = "<div class='gameicn gameicn-" + top5[game]['rank'] + "'><a href='" + top5[game]['game_page'] + "' target='_blank'>";
		d += "<img src='" + top5[game]['icon_url'] + "'/></a></div>";
		$('#top5icons').append(d);
	}

	//Generate Game lists
	for (game in bot5){
		var p = "<p>" + bot5[game]['rank'] + ". " + bot5[game]['name'] + "<br><span>Played " + bot5[game]['playtime_hours'] + " hrs.";
		p += bot5[game]['pct_complete'] + "% Completed.</span></p>";
		$('._text-6').append(p);
	}
	//generate image icons
	for (game in bot5){
		var d = "<div class='gameicn gameicn-" + bot5[game]['rank'] + "'><a href='" + bot5[game]['game_page'] + "' target='_blank'>";
		d += "<img src='" + bot5[game]['icon_url'] + "'/></a></div>";
		$('#bot5icons').append(d);
	}

	return 
}

