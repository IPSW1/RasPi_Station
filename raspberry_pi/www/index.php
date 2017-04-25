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
	// read weather data and time from textfile
	header('Content-Type: text/html; charset=UTF-8');
	$weather_data_file = fopen("/var/www/html/current_data.txt", "r") or die("Unable to open file!");
	$weather_data_str = fread($weather_data_file, filesize("/var/www/html/current_data.txt"));
	$weather_data_arr = split(";", $weather_data_str);
	fclose($weather_data_file);
?>

<br></br>
	<!-- HTML table to display weatherdata -->
	<table align="center">
		<tr>
			<td align="center" width=280><div class = "data"><?php echo $weather_data_arr[0];?></div></td>
			<td align="center" width=280><div class = "data"><?php echo $weather_data_arr[1];?></div></td>
			<td align="center" width=280><div class = "data"><?php echo $weather_data_arr[2];?></div></td>
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

<!-- display forecast -->
<div class = "forecast">Forecast: <?php echo $weather_data_arr[3];?></div>
<br></br>
<br></br>

<!-- style switcher and display of time of last update -->
<div align='center'>
		<a href="#" onclick="setActiveStyleSheet('default'); return false;">Dark</a>&nbsp &nbsp <a href="#" onclick="setActiveStyleSheet('alternate'); return false;">Light</a>
		<p></p>
		<div class = "label">Last update: <?php echo $weather_data_arr[4];?></div>
</div>

<br></br>
<br></br>

<div align='center'>
	<script src='http://openweathermap.org/themes/openweathermap/assets/vendor/owm/js/d3.min.js'></script><div id='openweathermap-widget'></div>
	<script type='text/javascript'>

	// your city id and api key
	var cityId = 2950159	// example for Berlin
	var apiKey = 'your-api-key'

        window.myWidgetParam = {
            id: 21,
            cityid: cityId,
            appid: apiKey,
            units: 'metric',
            containerid: 'openweathermap-widget',                        
        };
        (function() {
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.async = true;
            script.src = 'http://openweathermap.org/themes/openweathermap/assets/vendor/owm/js/weather-widget-generator.js';
            var s = document.getElementsByTagName('script')[0];
            s.parentNode.insertBefore(script, s);
        })();
	</script>
</div>

</body>
</html>
