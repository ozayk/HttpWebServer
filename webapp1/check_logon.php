<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "userDB";

$conn = mysqli_connect($servername, $username, $password, $dbname);
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

$sql = "SELECT id FROM my_users WHERE username = '$argv[1]' and password = '$argv[2]'";
$result = mysqli_query($conn,$sql);
$row = mysqli_fetch_array($result,MYSQLI_ASSOC);
$count = mysqli_num_rows($result);

if ($count == 1) {
	echo "1";
} else {
	echo "0";
}

$conn->close();
?>
