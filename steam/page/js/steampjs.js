/*steamjson.js
 *This file contains the functions needed for getting information from the Steam API
 *This will be used by the steam playtime VGstats test by Curtis and Ryan Quintal
 */
var baseURL = "http://api.steampowered.com/";
var profileSummaryURL = "ISteamUser/GetPlayerSummaries/v0002/?";
var ownedGamesURL = "IPlayerService/GetOwnedGames/v0001/?";
var achievementsURL = "ISteamUserStats/GetPlayerAchievements/v0001/?";
var recentlyPlayedURL = "IPlayerService/GetRecentlyPlayedGames/v0001/?";

function timeString(mins) {
	var months = mins / 43829;
	if (months >= 1) {
		return ("" + months.toFixed(2) + " Months");
	}
	var weeks = mins / 10080;
	if (weeks >= 1) {
		return ("" + weeks.toFixed(2) + " Weeks");
	}
	var days = mins / 1440;
	return ("" + days.toFixed(3) + " Days");
}

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
		info['appid'] = top_games[game]['appid'];
		info['rank'] = parseInt(game) + 1;
		info['icon_url'] = 'http://media.steampowered.com/steamcommunity/public/images/apps/' + top_games[game]['appid'] + '/' + top_games[game]['img_icon_url'] + '.jpg';
		info['game_page'] = 'http://store.steampowered.com/app/' + top_games[game]['appid'];
		listVals.push(info)
	}
	
	var allinfo = {}
	allinfo['total_playtime_min'] = total_mins;
	allinfo['total_playtime_hours'] = Math.round(total_mins / 60);
	allinfo['total_playtime_string'] = timeString(total_mins);
	allinfo['top10'] = listVals;
	console.log(allinfo)
	return allinfo
}

function getListAchievements(gamelist) {
	for (game in gamelist) {
		var total_achvs = 0;
		var comp_achvs = 0;
		achievs = getGameAchievements(key, id, gamelist[game]['appid']);
		for (achv in achievs['achievements']) {
			total_achvs++;
			if (achievs['achievements'][achv]['achieved'] == 1) {
				comp_achvs++;
			}	
		}
		gamelist[game]['total_achvs'] = total_achvs;
		gamelist[game]['comp_acvs'] = comp_achvs;
		gamelist[game]['pct_complete'] = Math.round((comp_achvs / total_achvs) * 100) || "NA";
	}
	return gamelist;
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

function checkError() {
	var error = getParameterByName('error');
	var steamsite = "'steamcommunity.com'";
	if(error == "") {
		return;
	}
	if(error == "nopage") {
		$('#iderror').text("ERROR - No web page was found at the URL you entered. Make sure the URL contains " + steamsite);
	}
	if(error == "noprofile") {
		$('#iderror').text("ERROR - The URL you entered is not a valid Steam Profile Page. Make sure the URL contains " + steamsite);
	}
	return;
}

/*Test out API json fetching functions
 */
function getStats() {
	console.log("start all");
	var newid = getParameterByName('steamid');
	if (newid != "") {
		id = newid;
	} else {
		//No Steam ID entered return in error
	}

	key = "";
	
	//get profile info
	var profileinfo = getProfileSummary(key, id);
	console.log(profileinfo);
	if(jQuery.isEmptyObject(profileinfo)) {
		//couldnt aquire profile info return in error
	}
	//get playtime info
	var playinfo = playtimeTotal(key, id);
	console.log(playinfo);
	if(jQuery.isEmptyObject(playinfo)) {
		//couldnt aquire game info return in error
	}
	var top5 = playinfo['top10'].slice(0,5);
	var bot5 = playinfo['top10'].slice(5,10);
	//Replace headline text
	$('#mainhead').text("You've played " + playinfo['total_playtime_hours'] + " hours of games.");
	$('#subhead').text("That's " + playinfo['total_playtime_string'] + " of games, " + profileinfo['personaname'] + ".");
	//profileinfo['profileurl'] is players page
	//profileinfo['personastate'] is status 0- offline 1-online 2-busy 3-away 4-snooze 5-looking to trade 6-looking to play
	//profileinfo['avatarfull'] 184x184px avatar
	//profileinfo['avatarmedium'] 64x64px avatar
	//profileinfo['timecreated'] time since epoch account was created PRIVATE INFO
	
	//Generate Game lists
	for (game in top5){
		var element = "<div class='game game-" + top5[game]['rank'] + "'>";
		element += "<a href='" + top5[game]['game_page'] + "'><img class='gameicn' src='" + top5[game]['icon_url'] + "'></a>";
		element += "<p class='gamename' id='game" + top5[game]['appid'] + "'>" + top5[game]['name'] + "<br><span>" + top5[game]['playtime_hours'] + " hrs. &#8226; " + "?% Completed.</span></p></div>";
		$('.1-left').append(element);
	}

	//Generate Game lists
	for (game in bot5){
		var element = "<div class='game game-" + bot5[game]['rank'] + "'>";
		element += "<a href='" + bot5[game]['game_page'] + "'><img class='gameicn' src='" + bot5[game]['icon_url'] + "'></a>";
		element += "<p class='gamename' id='game" + bot5[game]['appid'] + "'>" + bot5[game]['name'] + "<br><span>" + bot5[game]['playtime_hours'] + " hrs. &#8226; " + "?% Completed.</span></p></div>";
		$('.2-right').append(element);
	}

	//Now replace elements with achievement info
	getListAchievements(top5);
	for (game in top5){
		var gameid = "#game" + top5[game]['appid'];
		var newgame = "<p class='gamename' id='game" + top5[game]['appid'] + "'>" + top5[game]['name'] + "<br><span>" + top5[game]['playtime_hours'] + " hrs. &#8226; " + top5[game]['pct_complete'] + "% Completed.</span></p></div>";
		$(gameid).replaceWith(newgame);
	}
	getListAchievements(bot5);
	for (game in bot5){
		var gameid = "#game" + bot5[game]['appid'];
		var newgame = "<p class='gamename' id='game" + bot5[game]['appid'] + "'>" + bot5[game]['name'] + "<br><span>" + bot5[game]['playtime_hours'] + " hrs. &#8226; " + bot5[game]['pct_complete'] + "% Completed.</span></p></div>";
		$(gameid).replaceWith(newgame);
	}
	
	return;
}
