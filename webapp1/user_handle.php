<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "userDB";

if ($argc == 4) {
$conn = mysqli_connect($servername, $username, $password);
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

$sql = "CREATE DATABASE IF NOT EXISTS userDB";
if (mysqli_query($conn, $sql)) {
} else {
    echo "0";
}

mysqli_close($conn);

$conn = mysqli_connect($servername, $username, $password, $dbname);
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

$sql = "CREATE TABLE IF NOT EXISTS my_users (
id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(30) NOT NULL,
password VARCHAR(30) NOT NULL,
email VARCHAR(50),
reg_date TIMESTAMP
)";

if (mysqli_query($conn, $sql)) {
} else {
   echo "0";
}

mysqli_close($conn);

$conn = new mysqli($servername,$username,$password,$dbname);
    
if ($conn->connect_errno) {
         die("ERROR : -> ".$conn->connect_error);
     }

 $uname = $argv[1];
 $email = $argv[2];
 $upass = $argv[3];
 
 $uname = $conn->real_escape_string($uname);
 $email = $conn->real_escape_string($email);
 $upass = $conn->real_escape_string($upass);
 
 
 $check_email = $conn->query("SELECT email FROM my_users WHERE email='$email'");
 $count=$check_email->num_rows;
 
 if ($count==0) {
  
  $query = "INSERT INTO my_users(username,email,password) VALUES('$uname','$upass','$email')";

  if ($conn->query($query)) {

	echo "1";
  }else {

	echo "-1";
  }
  
 }else {
	echo "0";
}
 
 $conn->close();

}elseif($argc == 3) {

$conn = new mysqli($servername,$username,$password,$dbname);
    

 $uname = $argv[1];
 $email = $argv[2];
 
 $uname = $conn->real_escape_string($uname);
 $email = $conn->real_escape_string($email);
 
 
 $check_user = $conn->query("SELECT username FROM my_users WHERE username='$uname'");
 $count=$check_user->num_rows;
 
 if ($count==0) {
 
	echo "0";
} else {

$sql = "UPDATE my_users SET email='$email' WHERE username='$uname'";
if (mysqli_query($conn, $sql)) {
   echo "1";
} else {
   echo "0";
}

}
$conn->close();
} elseif($argc == 2) {

	$conn = new mysqli($servername, $username, $password, $dbname);
	$uname = $argv[1];
	
	$uname = $conn->real_escape_string($uname);
$sql = "DELETE FROM my_users WHERE username='$uname'";

if (mysqli_query($conn, $sql)) {
	echo "1";

} else {

	echo "0";
}
 $conn->close();

} else {

echo "0";
}
?>
