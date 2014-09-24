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

/* Takes api key and steam id
 * returns object with user's steam profile info
 */
function getProfileSummary(apiKey, userId) {

	var url = baseURL + profileSummaryURL + "&steamids=" + userId;
	console.log("Requesting: " + url);
	var mydata = {};
	$.ajax({
		url: "./proxy.php",
		async: true,
		dataType: 'json',
		data: { requrl: url },
		success: function (json) {
			mydata = json["response"]["players"][0];
			console.log("Success Func");
			console.log(json);
			getOwnedGames(key, id, mydata);
		},
		error: function() {
			console.log("ERROR FUNC");
		}
	});
	console.log("Request finished");
	return mydata;
}

/* Takes api key and steam id
 * returns object with user's owned game list
 */
function getOwnedGames(apiKey, userId, profileinfo) {

	var url = baseURL + ownedGamesURL + "&steamid=" + userId;
	url += "&include_appinfo=1" + "&include_played_free_games=1";
	console.log("Requesting: " + url);
	var mydata = {};
	$.ajax({
		url: "./proxy.php",
		async: true,
		dataType: 'json',
		data: { requrl: url },
		success: function (json) {
			console.log("Succes func, getownedGames");
			console.log(json);
			var data = json["response"];
			var playinfo = playtimeTotal(data);
			$("#mainhead").fadeOut(function() {
				$(this).text("You've played " + playinfo['total_playtime_hours'] + " hours of games.");
			}).fadeIn(2500);
			$("#subhead").fadeOut("slow", function() {
				$(this).text("That's " + playinfo['total_playtime_string'] + " of games, " + profileinfo['personaname'] + ".");
			}).fadeIn(5000);
			//Now display Game List
	
			var top5 = playinfo['top10'].slice(0,5);
			var bot5 = playinfo['top10'].slice(5,10);
	
			//Generate Game lists
			for (game in top5){
				var element = "<div class='game game-" + top5[game]['rank'] + "'>";
				var gid = "gid" + top5[game]['appid'];
				element += "<a href='" + top5[game]['game_page'] + "'><img class='gameicn' src='" + top5[game]['icon_url'] + "'></a>";
				element += "<p class='gamename' id='game" + top5[game]['appid'] + "'>" + top5[game]['rank'] + ". " + top5[game]['name'] + "<br><span id='" + gid + "'>" + top5[game]['playtime_hours'] + " hrs. &#8226; " + "?% Completed.</span></p></div>";
				$('.1-left').append($(element).hide().delay(1800).fadeIn(2500));
				getGameAchievements(key, id, top5[game]['appid'], top5[game]['playtime_hours']);
			}

			//Generate Game lists
			for (game in bot5){
				var element = "<div class='game game-" + bot5[game]['rank'] + "'>";
				var gid = "gid" + bot5[game]['appid'];
				element += "<a href='" + bot5[game]['game_page'] + "'><img class='gameicn' src='" + bot5[game]['icon_url'] + "'></a>";
				element += "<p class='gamename' id='game" + bot5[game]['appid'] + "'>" + bot5[game]['rank'] + ". " + bot5[game]['name'] + "<br><span id='" + gid + "'>" + bot5[game]['playtime_hours'] + " hrs. &#8226; " + "?% Completed.</span></p></div>";
				$('.2-right').append($(element).hide().delay(1800).fadeIn(2500));
				getGameAchievements(key, id, bot5[game]['appid'], top5[game]['playtime_hours']);
			}
			return;
		}
	});
	console.log("Request finished");
	return mydata;
}

/* Takes api key and steam id
 * returns object with user's owned game list
 */
function getGameAchievements(apiKey, userId, appid, hours) {

	var url = baseURL + achievementsURL + "&steamid=" + userId;
	url += "&appid=" + appid;
	console.log("Requesting: " + url);
	var mydata = {};
	$.ajax({
		url: "./proxy.php",
		async: true,
		dataType: 'json',
		data: { requrl: url },
		success: function (json) {
			mydata = json["playerstats"];
			console.log("ACHVS| ID-" + appid + " HRS-" + hours);
			var gid = "#gid" + appid;
			var total_achvs = 0;
			var comp_achvs = 0;
			for (achv in mydata['achievements']) {
				total_achvs++;
				if (mydata['achievements'][achv]['achieved'] == 1) {
					comp_achvs++;
				}	
			}
			var pctComplete = Math.round((comp_achvs / total_achvs) * 100) || "NA";
			$(gid).replaceWith("<span>" + hours + " hrs. &#8226; " + pctComplete + "% Completed.</span>");
			console.log("ACHVS| ID-" + appid + " HRS-" + hours + " PCT-" + pctComplete);
		},
		error: function(xhr, ajaxOptions, thrownError) {
			console.log("ERROR ACHVS");
			console.log("xhr.status");
			console.log("thrownError");
		}
	});
	console.log("Request finished- GetAchvs");
	return mydata;
}

function compare_playtime(a,b) {
	if(a['playtime_forever'] < b['playtime_forever'])
		return -1;
	if(a['playtime_forever'] > b['playtime_forever'])
		return 1;
	return 0;
}

function playtimeTotal(data) {
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
	
	//get profile info, this kicks off getting rest of indo async
	var profileinfo = getProfileSummary(key, id);
	return;
}
