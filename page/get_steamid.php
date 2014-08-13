<?php
#Taken from StackOverflow http://stackoverflow.com/questions/2762061/how-to-add-http-if-its-not-exists-in-the-url
function addhttp($url) {
  if (!preg_match("~^(?:f|ht)tps?://~i", $url)) {
    $url = "http://" . $url;
  }
  return $url;
}

#Add http:// to url if needed
$url = $_GET['steamid'];
$url = addhttp($url);

#get contents of url return in error if no page found
$file = file_get_contents($url);
if($file === FALSE){
  $location = "/page/index.html?error=nopage";
  header("Location: " . "http://" . $_SERVER['HTTP_HOST'] . $location); 
  exit();
}

#grab steam id if pge foud
$arr = explode('steamid":"', $file);
$steamid = $arr[1];
$arr = explode('",', $steamid);
$steamid = $arr[0];

#If no steam id string then page was not proper steam profile page
if($steamid == "") {
  $location = "/page/index.html?error=noprofile";
  header("Location: " . "http://" . $_SERVER['HTTP_HOST'] . $location);
  exit();
}

#If everything was good load results page with steamid param
$location = "/page/results.html?steamid=" . $steamid;
header("Location: " . "http://" . $_SERVER['HTTP_HOST'] . $location);
exit();

?>
