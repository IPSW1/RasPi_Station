#!usr/bin/python

import time, sys, os
import httplib, urllib
import MySQLdb
import tweepy
from bluetooth import *

################	Configuration ###############
#Bluetooth
mac = ''

#MySQL data
db = MySQLdb.connect(host="",
					user="",
					passwd="",
					db="")
table = ""	#Table name
dt = ""	#Column name for datetime
cur = db.cursor()

#Twitter API
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

#Pushover data
push_token = ""
push_user = ""
push_title = "Weather station"
################################################

def main():
	twit_counter = 6

	current_time_sec = 0
	time_since_push = 0
	push_time_sec = 0

	#Establish a Bluetooth connection
	sensor = BluetoothSocket(RFCOMM)
	print "Establish a Bluetooth connection"
	sensor.connect((mac, 1))
	print "Connection establishment successful"

	#Additional functions default states
	pushes = False
	twitter = False

	#Ckeck parameters
	for command in sys.argv:
		if command == "-p":
			pushes = True
			print "Push enabled"
		elif command == "-t":
			twitter = True
			print "Twitter enabled"

	#Twitter authentification
	global twit_api
	if twitter:
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		twit_api = tweepy.API(auth)
		print "Twitter account linked"

	print "\n\n"


	while True:
		try:
			receive = ' '
			output = ''

			#Receiving data until the last character is a line break
			while receive[len(receive) - 1] != '\n':
				receive = sensor.recv(20)
				output = output + receive

			print "Received data: " + output[:-1]

			#Remove last character (line break) of the finished string an split the string by ';'
			output = output[:-1]
			data = output.split(";", 3)

			#Execute main functions
			forecast = doForecast()
			logger(output, forecast)
			if twitter:
				if twit_counter >= 5:
					twitter_post(data)
					twit_counter = 0
				else:
					twit_counter += 1
			if pushes:
				current_time_sec = time.mktime(time.localtime())
				time_since_push = current_time_sec - push_time_sec

				#Send push messages only every 10 hours
				if time_since_push >= 36000:
					temp_alert(output)
					push_time_sec = time.mktime(time.localtime())


			print "{}{}".format(40 * "-", "\n")
		except:
			if db:
				db.close()
			if pushes:
				push("Something went wrong, the connection is interrupted.")
			sys.exit()


def logger(entry, forecast):
	entry = entry.split(";", 3)
	datetime = time.strftime('%Y-%m-%d %H:%M:%S')

	#Read out the number of entries
	count_query = "SELECT COUNT(*) FROM {}".format(table)
	cur.execute(count_query)
	quantity = cur.fetchone()[0]

	#Keep the number of entries at a maximum of 10000
	if quantity >= 10000:
		with db:
			delete_query = "DELETE FROM {} WHERE(SELECT {} ORDER BY {}) LIMIT 1".format(table, dt, dt)
			cur.execute(delete_query)

	with db:
		#Insert the latest data into the table
		insert_query = "INSERT INTO {} VALUES (%s, %s, %s, %s, %s)".format(table)
		insert_data = (datetime, entry[0], entry[1], entry[2], forecast)
		cur.execute(insert_query, insert_data)

	print "Generated log entry " + time.ctime()


def doForecast():
	difference = calculateBiggestDifference()
	forecast = ausgabe(difference)
	return forecast


def calculateBiggestDifference():
	try:
		#Fetch number of entries in the table
		count_query = "SELECT COUNT(*) FROM {}".format(table)
		cur.execute(count_query)
		line_number = cur.fetchone()[0]

		#Set the number of lines to read out to a maximum of 16 hours
		if (line_number < 96):
			readout_lines = line_number - 1
		else:
			readout_lines = 96

		#Fetch data from table
		with db:
			fetch_query = "SELECT * FROM {} ORDER BY {} DESC LIMIT {}".format(table, dt, readout_lines)
			cur.execute(fetch_query)
			data = cur.fetchall()

		#Calculate average of the last 3 values to smooth measuring errors
		x = 0
		total = 0
		while x < 3:
			total = total + data[x][3]
			x = x + 1

		avg = total / x

		#Calculate biggest difference between two values, for positive and negative values
		i = 10
		positive_value = 0
		negative_value = 0

		while i < readout_lines:
			difference = avg - data[i][3]
			if (difference > 0):
				if (difference > positive_value):
					positive_value = difference
			elif (difference < 0):
				if (difference < negative_value):
					negative_value = difference
			i = i + 2

		#Select the most significant difference
		if positive_value > -negative_value:
			return positive_value
		elif positive_value < -negative_value:
			return negative_value
		elif positive_value == -negative_value:
			return 0

	except:
		return -99


def ausgabe(wert):
	#Choose weather forecast
	#The values are set completely by instinct and observation, so feel free to improve them
	if wert > 0 and wert < 50:
		if wert <= 1:
			forecast = "Stable weather conditions"
		elif wert <= 4 and wert > 1:
			forecast = "Small weather improvement"
		elif wert <= 7 and wert > 4:
			forecast = "Strong weather improvement"
		elif wert > 7:
			forecast = "Extreme weather improvement"

	elif wert < 0 and wert > -50:
		if wert >= -1:
			forecast = "Stable weather conditions"
		elif wert >= -4 and wert < -1:
			forecast = "Small weather deterioration"
		elif wert >= -7 and wert < -4:
			forecast = "Strong weather deterioration"
		elif wert < -7:
			forecast = "Extreme weather deterioration"

	elif wert == 0:
		forecast = "Stable weather conditions"

	elif wert == -99:
		forecast = "No forecast possible"

	else:
		forecast = "Error"

	print "Pressure difference: " + str(wert)
	print "Calculated forecast: " + forecast
	return forecast


def twitter_post(data_list):
	try:
		#Compose and string and tweet it
		post = "Temperature: " + str(data_list[0]) + "\nHumidity: " + str(data_list[1]) + "\nPressure: " + str(data_list[2])
		twit_api.update_status(status=post)
		twitter_minutes_remaining = 60
		print "Twitter post successful"
	except:
		print "Twitter post failed"


def temp_alert(data):
	part_data = data.split(";", 3)
	temp = float(part_data[0])

	#These are the values that have to be reached to get a push message
	#Of course they can be changed, and humidity and pressure can be used
	if temp < -10:
		push("The temperature is under -10C")
	elif temp < -5:
		push("The temperature is under -5C")
	if temp > 32:
		push("Temperature reached 32C")


def push(push_message):
	#This is a slightly modified version of the sample code from Pushover
	#Additional information: https://pushover.net/faq#library-python
	conn = httplib.HTTPSConnection("api.pushover.net:443")
	conn.request("POST", "/1/messages.json",
	urllib.urlencode({
		"token": push_token,
		"user": push_user,
		"title": push_title,
		"message": push_message,
	}), { "Content-type": "application/x-www-form-urlencoded" })
	conn.getresponse()

	print "Sent push"


if __name__ == "__main__":
	main()
