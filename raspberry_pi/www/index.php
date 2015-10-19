<html>
	<head>
		<title>Weather station</title>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<link rel="stylesheet" type="text/css" href="css/dark.css" title="default" />
		<link rel="alternate stylesheet" type="text/css" href="css/light.css" title="alternate" />
		<script type="text/javascript" src="/scripts/styleswitcher.js"></script>
	</head>

<body>
<?php
	//MySQL userdata
	$username = "";
	$password = "";
	$hostname = "";
	$db = "";
	$db_table = "";

	//Variables that should match the SQL columns
	$temp = "temp";
	$hum = "hum";
	$press = "press";
	$forec = "forecast";
	$datetime = "dtime";

	//Connect to MySQL and select database
	$connection = mysql_connect($hostname, $username, $password) or die("Unable to connect to MySQL");
	mysql_select_db($db) or die("Database does not exist");

	header('Content-Type: text/html; charset=UTF-8');

	//Daten aus Datenbank fuer aktuelle Daten abfragen
	$query = "SELECT * FROM ".$db_table." ORDER BY ".$datetime." DESC LIMIT 1";
	$return = mysql_query($query);
	$data = mysql_fetch_array($return);
?>
<br></br>
	<!-- HTML table to display weatherdata -->
	<table align="center">
		<tr>
			<td align="center" width=280><div class = "data"><?php echo round($data[$temp]);?></div></td>
			<td align="center" width=280><div class = "data"><?php echo round($data[$hum]);?></div></td>
			<td align="center" width=280><div class = "data"><?php echo round($data[$press]);?></div></td>
		</tr>
		<tr>
			<td align="center" height=1><table align="center"><tr><td align="center" height=1 width=200 style="border-bottom: 1px solid #aaaaaa"></td></tr></table></td>
			<td align="center" height=1><table align="center"><tr><td align="center" height=1 width=200 style="border-bottom: 1px solid #aaaaaa"></td></tr></table></td>
			<td align="center" height=1><table align="center"><tr><td align="center" height=1 width=200 style="border-bottom: 1px solid #aaaaaa"></td></tr></table></td>
		</tr>
		<tr>
			<td><div class = "label">Temperature in °C</div></td>
			<td><div class = "label">Humidity in %</div></td>
			<td><div class = "label">Pressure in hPa</div></td>
		</tr>
	</table>

<br></br>
<br></br>


<!-- Forecast -->
<div class = "forecast">Forecast: <?php echo $data[$forec];?></div>
<br></br>
<br></br>

<div align='center'>
		<a href="#" onclick="setActiveStyleSheet('default'); return false;">Dark</a>&nbsp &nbsp <a href="#" onclick="setActiveStyleSheet('alternate'); return false;">Light</a>
		<p></p>
		<div class = "label">Last update: <?php echo $data[$datetime];?></div>
</div>

</body>
</html>
