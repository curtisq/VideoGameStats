<?php
$key = trim(file_get_contents("./key.txt"));
$url = $_GET['requrl'] . "&key=" . trim($key);
$file = file_get_contents($url);

#file_put_contents("./phpout", "url-" . $url . " file: " . $file . "\n", FILE_APPEND);
echo $file;
?>
