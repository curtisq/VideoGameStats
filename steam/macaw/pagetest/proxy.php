<?php
$key = "80F844C6A71634409CA1946FDAA9A98C";
$url = $_GET['requrl'] . "&key=" . $key;
$file = file_get_contents($url);
echo $file;
?>
