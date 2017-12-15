<?php

// if it's a post request, set flag to 1
$passwordHash = json_decode(file_get_contents('credentials.json'))->passwordHash;
if (array_key_exists('turnOnPorts', $_POST) && password_verify($_POST['password'], $passwordHash)) {
	file_put_contents('turn_on_ports', '1');
}

// return response JSON with current flag value
header('Content-Type: application/json');
echo json_encode([
	'turnOnPorts' => file_exists('turn_on_ports')
]);

// after GET request remove file => flag to 0
if ($_SERVER['REQUEST_METHOD'] == 'GET') {
	@unlink('turn_on_ports');
}
