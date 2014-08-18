<?php
$key = "XXXXXXXX"; #Your Steam API Key here
$url = $_GET['requrl'] . "&key=" . trim($key);
$file = file_get_contents($url);

echo $file;
?>
