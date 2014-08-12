<?php
$key = file_get_contents("./key.txt");
$url = $_GET['requrl'] . "&key=" . $key;
$file = file_get_contents($url);
echo $file;
?>
