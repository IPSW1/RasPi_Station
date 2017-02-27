# Raspberry Pi Weather Station

This is (yet another) version of a weather station based on a Raspberry Pi.  
It provides data for temperature, humidity and air pressure which are available via a nice web interface.  
The sensors aren't directly attached to the Pi, but instead the data is meassured by an Arduino and transfered over 2.4GHz modules. In addition it also tries to calculate a forecast based on the pressure history.

##Features
* Measurement for temperature, humidity and air pressure about every 10 minutes
* (Very) Simple forecast calculation
* Providing data over pure and shiny designed web interface
* Twitter support
* Data upload to https://data.sparkfun.com

##Base station (Raspberry Pi)  
###Hardware  
The base station is a Raspberry Pi. It uses a NRF24L01 module to receive data from the remote sensor.
###Software
The base station runs the standard Raspbian Jessie distribution (https://www.raspberrypi.org/downloads/raspbian/). To connect to the Arduino sensor and collect the data, a Python script is permanently running in the background. It receives data, calculates the forecast and optionally posts it to Twitter (use argument `-t` after script call) and uploads it to Sparkfun (argument `-s`).  
The values are provided by a web interface written in HTML/PHP. Two CSS files and a Javascript style switcher give it a proper design. Apache is used as the server.  

**Dependencies:**  
&nbsp;&nbsp;&nbsp;**Python libraries:**  
  * RF24 (https://github.com/TMRh20/RF24)  
   -> including Python wrapper (http://tmrh20.github.io/RF24/Python.html)
  * Tweepy (https://github.com/tweepy/tweepy) (optional)

&nbsp;&nbsp;&nbsp;**Other:**  
  * Apache web server (https://httpd.apache.org)
  * PHP (http://php.net)

##Remote sensor (Arduino)
###Hardware
The remote sensor is based on an Arduino Nano. It uses a Bosch BMP280 to measure temperature and air pressure and a DHT22 for humidity. Data transfer is done by the same NRF24L01 module used in the base station.

###Software
The sketch running on the Arduino reads the sensor values, sends it over SPI to the NRF24L01 module and sleeps for about 10 minutes. The library for this is not very accurate, but exact timing is not required here.
  
**Dependencies:**  
&nbsp;&nbsp;&nbsp;**Arduino libraries:** 
  * Adafruit BMP280 (https://github.com/adafruit/Adafruit_BMP280_Library)
  * DHTlib (https://github.com/RobTillaart/Arduino/tree/master/libraries/DHTlib)
  * RF24 (https://github.com/TMRh20/RF24)
  * LowPower (https://github.com/rocketscream/Low-Power)
