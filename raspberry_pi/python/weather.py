#!usr/bin/python

import time, sys, os
import RPi.GPIO as GPIO
from RF24 import *

# only import libraries for Twitter and Sparkfun if option enabled
global twitter, sparkfun
twitter = False
sparkfun = False
for command in sys.argv:
	if command == "-t":
		twitter = True
		import tweepy
		print("Twitter enabled")
	if command == "-s":
		sparkfun = True
		import http.client, urllib
		print("Sparkfun enabled")


################ Configuration ###############
# RF24 setup
irq_gpio_pin = None
pipe_address = 0xF1F2F3F4E1 	# random addresses
radio = RF24(22, 0) 	# create RF24 entity
channel = 105

radio.begin()
radio.setDataRate(RF24_250KBPS);	# lower data rate to increase range
radio.setChannel(channel);
radio.enableDynamicPayloads()
radio.openReadingPipe(1, pipe_address)
radio.startListening()

# pressure history data
pressure_history = []
pressure_maxsize = 96

# sparkfun data
sf_public_ley = ""
sf_priavte_key = ""

# twitter data
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
location_id = '' 	# twitter location ID to add location to tweets (remove in function twitter_post if not needed)
################################################

def main():
	twit_counter = 6	# post intervall, corresponds to multiples of 10 minutes
	#twitter = False		# default value for Twitter posts
	#sparkfun = False	# default value for Sparkfun upload

	# twitter authentification
	global twit_api
	if twitter:
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		twit_api = tweepy.API(auth)
		print("Twitter account linked")

	# main loop
	while True:
		# do nothing if no data comes in
		while not radio.available():
		    pass
		# if data is availabe
		while radio.available():
		    len = radio.getDynamicPayloadSize()
		    receive_payload = radio.read(len)
		    receive_payload = receive_payload.decode('utf-8')
		    receive_payload = receive_payload.replace('\x00', '')	# filter out null characters

		print('Received data: {}'.format(receive_payload))

		# split the string by ';' to get separate values
		data = receive_payload.split(";", 3)

		# execute main functions
		process_new_data(data)
		forecast = do_forecast()
		if sparkfun:
			sparkfun_logger(data)
		if twitter:
			if twit_counter >= 5:
				twitter_post(data, forecast)
				twit_counter = 0
			else:
				twit_counter += 1

		print("{}{}".format(40 * "-", "\n"))

def process_new_data(weather_data):
	# write new data to file
	data_file = open("/var/www/html/current_data.txt", 'w')
	data_string = "{};{};{}\n".format(round(float(weather_data[0])), round(float(weather_data[1])), round(float(weather_data[2])))
	data_file.write(data_string)
	data_file.close()

	# keep track of pressure history
	if(len(pressure_history) > pressure_maxsize - 1):
		pressure_history.pop(0)
	pressure_history.append(float(weather_data[2]))

def sparkfun_logger(weather_data):
	try:
		conn = http.client.HTTPSConnection("data.sparkfun.com")
		conn.request("POST", "/input/{}".format(sf_public_ley),
		urllib.parse.urlencode({
		    "temp": weather_data[0],
		    "humidity": weather_data[1],
		    "pressure": weather_data[2],
		    }), { "Content-type": "application/x-www-form-urlencoded", "Connection": "close", "Phant-Private-Key": sf_priavte_key})
		conn.getresponse()

		print("Log entry to Sparkfun successful")

	except:
		print("Log entry to Sparkfun failed")


def do_forecast():
	difference = calculate_biggest_difference()
	forecast = choose_forecast(difference)
	return forecast


def calculate_biggest_difference():
	# just do a forecast if at least 10 values recorded
	if(len(pressure_history) < 10):
		return -99

	else:
		# calculate average of the last 3 values to smooth measuring errors
		index = len(pressure_history) - 1
		total = 0
		for i in range(0, 3):
			total = total + pressure_history[index - i]
		avg = total / 3

		# calculate biggest difference between two values, for positive and negative values
		i = len(pressure_history) - 1
		positive_value = 0
		negative_value = 0

		while i >= 0:
			difference = avg - pressure_history[i]
			if (difference > 0):
				if (difference > positive_value):
					positive_value = difference
			elif (difference < 0):
				if (difference < negative_value):
					negative_value = difference
			i = i - 1

		# select the most significant difference
		if positive_value > -negative_value:
			return positive_value
		elif positive_value < -negative_value:
			return negative_value
		elif positive_value == -negative_value:
			return 0


def choose_forecast(difference):
	# choose weather forecast
	# the values are set completely by instinct and observation, so feel free to improve them
	if difference > 0 and difference < 50:
		if difference <= 1:
			forecast = "0"
		elif difference <= 4 and difference > 1:
			forecast = "+"
		elif difference <= 7 and difference > 4:
			forecast = "++"
		elif difference > 7:
			forecast = "+++"

	elif difference < 0 and difference > -50:
		if difference >= -1:
			forecast = "0"
		elif difference >= -4 and difference < -1:
			forecast = "-"
		elif difference >= -7 and difference < -4:
			forecast = "--"
		elif difference < -7:
			forecast = "---"

	elif difference == 0:
		forecast = "0"

	elif difference == -99:
		forecast = "No forecast possible"

	else:
		forecast = "Error"

	print("Pressure difference: {}".format(difference))
	print("Calculated forecast: {}".format(forecast))
	return forecast


def twitter_post(weather_data, forecast):
	try:
		post = "Temp: {}\nHum: {} \nPres: {}\nForecast: {}".format(weather_data[0], weather_data[1], weather_data[2], forecast)
		twit_api.update_status(status=post, place_id=location_id)
		print("Twitter post successful")

	except:
		print("Twitter post failed")


if __name__ == "__main__":
	main()
