<h1>Links from beyond the Maelfroth</h1>


<table>
	<thead>
		<tr><th>Date</th><th>User</th><th>Message</th></tr>
	</thead>
	<tbody>
<?PHP

$tr = '<tr><td>%s</td><td>%s</td><td>%s</td></tr>';

$db = sqlite_open('../lampstand.db');

$query = "select * from urllist order by time desc limit 40";

$result = sqlite_query($query, $db);

while ($row = sqlite_fetch_array($result)){
	$time = date('r', $row['time']);
	$user = $row['username'];
	$message = nl2br(ereg_replace("[[:alpha:]]+://[^<>[:space:]]+[[:alnum:]/]","<a href=\"\\0\">\\0</a>", $row['message']));
	printf($tr, $time, $user, $message);
}


sqlite_close($db);

?>

</tbody>
</table>
