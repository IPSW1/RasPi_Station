# RasPi Station

This is (yet another) version of a weather station based on a Raspberry Pi.  
It provides data for temperature, humidity and air pressure which are available via a nice web interface.  
The sensors aren't directly attached to the Pi, but instead the data is collected by an Arduino and is sent over Bluetooth. In addition it also tries to calculate a forecast based on the pressure history.

##Features
* Measurement for temperature, humidity and air pressure about every 10 minutes
* Saving data in a SQL database
* (Very) Simple forecast calculation
* Providing data over pure and shiny designed web interface
* Twitter support
* Data upload to https://data.sparkfun.com

##Hardware
###Base station (Raspberry Pi)  
The base station is a Raspberry Pi. It uses a Bluetooth USB adapter to connect to the remote sensor.
###Sensor (Arduino)  
The remote sensor is based on an Arduino Nano board. It uses a DS18B20 to measure temperature, a DHT22 for humidity an a BPM180 for air pressure. It uses a HC-05 Bluetooth module for the connection.  

##Software
###Base station
The base station runs the standard Raspbian Jessie distribution (https://www.raspberrypi.org/downloads/raspbian/). To connect to the Arduino sensor and collect the data a Python script is permanently running in the background. It receives data, writes it to the SQL database (hosed on the Pi), calculates the forecast and posts it to Twitter.
Therefor it uses the following libraries:  
* Python-MySQL (former MySQLdb) (http://mysql-python.sourceforge.net/MySQLdb.html)
* Tweepy (https://github.com/tweepy/tweepy)
* PyBlueZ (https://github.com/karulis/pybluez)

The values are provided by a web interface written in HTML/PHP. Two CSS files and a Javascript style switcher give it a proper design. Apache is used as the server.

###Sensor
The sketch running on the Arduino reads the sensor values, sends it over the serial interface to the Bluetooth module and sleeps for about 10 minutes. The library for this is not very accurate, but it is not a problem here.
The following libraries are used:
* Wire, SoftwareSerial (included in the Arduino IDE)
* OneWire (http://playground.arduino.cc/Learning/OneWire)
* DallasTemperature (https://github.com/milesburton/Arduino-Temperature-Control-Library)
* DHTlib (https://github.com/RobTillaart/Arduino/tree/master/libraries/DHTlib)
* Adafruit Sensor and BMP085 library (https://learn.adafruit.com/bmp085/overview)
* LowPower (https://github.com/rocketscream/Low-Power)

##How to get it running
**1. Install required packages**
* Webserver (`apache2`)
* PHP (`php5`, `libapache2-mod-php5`)
* MySQL (`mysql-server`)
* `bluetooth`, `bluez` and `libluetooth-dev` for Bluetooth support

**2. Install Python libraries**  
At first, installing the Python libraries for SQL and Bluetooth (see above) is necessary. If you want to use Twitter the related library has to be installed.  

**3. Create database**  
To save the data a SQL database is required. It has to contain a table with the following format:  
dtime DATETIME, temp FLOAT, hum FLOAT, press FLOAT, forecast TEXT

**4. Create Sparkfun data stream**  
On data.sparkfun.com you can create a free stream where you can store the data. With the keys you get you will have access to manage
and upload to your stream.

**5. Prepare the script**  
At the beginning of the main Python script (`weather.py`) there are a few fields in which you have to insert the MAC address for the bluetooth module, the values for the SQL database (host, username, password, database), and API data for Sparkfun and Twitter.

**6. Get the Arduino ready**  
To get the Arduino started wire it up and set the pin numbers in the sketch so that data can be read. The DS18B20, DHT22 and HC-05 can be connected to any digital pin, you only have to change the sketch for the appropriate pins. Then upload the sketch and you are ready. The HC-05 module can be configured with AT commands, but this should not be necessary.  
***Note: You may can not connect the HC-05 directly to the Arduino because of the 3.3V serial level. So, if the module doesn't have a converter it will get damaged!***

**7. Set up the web interface**  
The content of the folder `raspberry_pi/www` must be copied in the web server directory. In the `index.php` page there are a few variables you have to set so that the webserver can connect to the SQL database. If you want a better looking font, you can download Open Sans here for free: http://www.fontsquirrel.com/fonts/open-sans-condensed  
Put the fonts it in a folder named fonts in the web server directory and it will look much better.

**8. Start measurement**  
Now you can try to get a connection to the Arduino by starting the Python script. To use Twitter use parameter `-t`  
You should be able to see the output on the terminal. If everything went fine there will be incoming data within 10 minutes after starting the script. The data can be looked up by navigating to your Raspberry Pi's IP address.
