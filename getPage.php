<?php
exec("genpdf.py");
echo "Page Generated."
$location = "/output/output.html"
header("Location: " . "http://" . $_SERVER['HTTP_HOST'] . $location);
?>
