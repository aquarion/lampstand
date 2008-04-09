<h1>Links from beyond the Maelfroth</h1>


<table>
	<thead>
		<tr><th>Date</th><th>User</th><th>Message</th></tr>
	</thead>
	<tbody>
<?PHP

$tr = '<tr><td>%s</td><td>%s</td><td>%s</td></tr>';

$db = new PDO('sqlite:/home/aquarion/projects/lampstand/lampstand.db');

$query = "select * from urllist order by time desc limit 40";

$result = $db->query($query);

while ($row = $result->fetch(PDO::FETCH_ASSOC)){
	$time = date('r', $row['time']);
	$user = $row['username'];
	$message = nl2br(ereg_replace("[[:alpha:]]+://[^<>[:space:]]+[[:alnum:]/]","<a href=\"\\0\">\\0</a>", $row['message']));
	printf($tr, $time, $user, $message);
}


?>

</tbody>
</table>
