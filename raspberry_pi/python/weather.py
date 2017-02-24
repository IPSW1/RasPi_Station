#!usr/bin/python

import time, sys, os
import httplib, urllib
import MySQLdb
import tweepy
import RPi.GPIO as GPIO
from RF24 import *

################ Configuration ###############
#RF24 setup
irq_gpio_pin = None
pipes = [0xF1F2F3F4E1, 0xF6F7F8F9D2] #random addresses
radio = RF24(22, 0) #create RF24 entity
radio.begin()
radio.enableDynamicPayloads()
radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1,pipes[0])


#MySQL data
db = MySQLdb.connect(host="",
					user="",
					passwd="",
					db="")
table = ""	#Table name
dt = ""	#Column name for datetime
cur = db.cursor()

#Sparkfun data
sf_public_ley = ""
sf_priavte_key = ""

#Twitter API
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
location_id = '' #Twitter location ID to add location to tweets (remove in function twitter_post if not needed)

################################################

def main():
	twit_counter = 6

	#Twitter default states
	twitter = False

	#Ckeck parameters
	for command in sys.argv:
		if command == "-t":
			twitter = True
			print("Twitter enabled")

	#Twitter authentification
	global twit_api
	if twitter:
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		twit_api = tweepy.API(auth)
		print("Twitter account linked")

	print "\n\n"


	while True:
		try:
			# do nothing if no data comes in
			
			while not radio.available():
			    pass
			# if data is availabe
			while radio.available():
			    len = radio.getDynamicPayloadSize()
			    receive_payload = radio.read(len)
			    receive_payload = receive_payload.decode('utf-8')
			    receive_payload = receive_payload.replace('\x00', '')	#filter out null characters

			print('Received data: {}'.format(receive_payload))

			#Split the string by ';' to get separate values
			data = receive_payload.split(";", 3)

			#Execute main functions
			forecast = doForecast()
			sparkfunLogger(output)
			logger(output, forecast)
			if twitter:
				if twit_counter >= 5:
					twitter_post(data, forecast)
					twit_counter = 0
				else:
					twit_counter += 1

			print "{}{}".format(40 * "-", "\n")

		except:
			if db:
				db.close()
			sys.exit()


def sparkfunLogger(data):
	try:
		data = data.split(";", 3)

		conn = httplib.HTTPSConnection("data.sparkfun.com")
		conn.request("POST", "/input/{}".format(sf_public_ley),
		urllib.urlencode({
	    	"temp": data[0],
	    	"humidity": data[1],
	    	"pressure": data[2][:-1],
			}), { "Content-type": "application/x-www-form-urlencoded", "Connection": "close", "Phant-Private-Key": sf_priavte_key})
		conn.getresponse()
	except:
		print("Log entry to Sparkfun failed")


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

	print("Generated log entry {}".format(time.ctime()))


def doForecast():
	difference = calculateBiggestDifference()
	forecast = chooseForecast(difference)
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


def chooseForecast(difference):
	#Choose weather forecast
	#The values are set completely by instinct and observation, so feel free to improve them
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


def twitter_post(data_list, forecast):
	try:
		post = "Temp: {}\nHum: {} \nPres: {}\nForecast: {}".format(data_list[0], data_list[1], data_list[2], forecast)
		twit_api.update_status(status=post, place_id=location_id)
		print("Twitter post successful")

	except:
		print("Twitter post failed")


if __name__ == "__main__":
	main()
