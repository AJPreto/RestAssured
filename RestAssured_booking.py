#!/usr/bin/env python

"""
Variables to be used to for the booking section of RestAssured API 
"""

__author__ = "A.J. Preto"
__email__ = "martinsgomes.jose@gmail.com"
__project__ = "RestAssured - Restaurant challenge"

import RestAssured_variables

def split_date(input_date_string, string_splitter = "-"):

	"""
	Split a user-provided date string into integer objects, retrieve a dictionary,
	"""
	date_list = [int(x) for x in input_date_string.split(string_splitter)]
	return {"year": date_list[0], "month": date_list[1], "day": date_list[2], "hour": date_list[3]}

def booking_overlapping(input_connection, date, check_mode = False, input_table_number = None):

	"""
	Retrieve the relevant objects for booking comparison.
	"check_mode" was added to enable checking whether the customer 
	had a previous booking or he commited a mistake. "check_mode" requires the input_table_number
	"""
	simultaneous_reservations = input_connection.execute("SELECT * FROM bookings WHERE year=? AND month=? AND day=? AND hour=?",\
				 (date["year"], date["month"], date["day"], date["hour"]))
	simultaneous_reservations_list = list(simultaneous_reservations)
	occupied_tables = [row[1] for row in simultaneous_reservations_list]
	unoccupied_tables = sorted(list(set(occupied_tables)^set(list(range(1, RestAssured_variables.MAX_TABLES + 1)))))
	if check_mode == True:
		if int(input_table_number) in occupied_tables:
			return input_connection, True
		elif int(input_table_number) not in occupied_tables:
			return input_connection, False

	elif check_mode == False:
		return simultaneous_reservations_list, occupied_tables, unoccupied_tables, input_connection

def insert_booking(input_connection, table_number, date):

	"""
	Introduce new entry in booking
	"""
	input_connection.execute("INSERT INTO bookings (table_id, year, month, day, hour) \
      				VALUES (?, ?, ?, ?, ?)", (table_number, date["year"], date["month"], \
      					date["day"], date["hour"]))
	return input_connection

def delete_booking(input_connection, table_number, date):

	"""
	Introduce new entry in booking
	"""
	input_connection.execute("DELETE FROM bookings WHERE table_id=? AND year=? AND month=? AND day=? AND hour=?", \
						(table_number, date["year"], date["month"], date["day"], date["hour"]))
	return input_connection

def assess_work_hours(input_hour):
	
	"""
	Confirm whether the input hour fits the workhours or not
	"""
	if input_hour not in RestAssured_variables.WORKING_HOURS_INTERVALS:
		return False, {"Error": "The restaurant is not working at that time, please pick a time for lunch between " + \
				str(RestAssured_variables.WORKHOURS_DICTIONARY["lunch_start"]) + "h and " + str(RestAssured_variables.WORKHOURS_DICTIONARY["lunch_end"]) + \
				"h or, for dinner, between " + \
				str(RestAssured_variables.WORKHOURS_DICTIONARY["dinner_start"]) + "h and " + str(RestAssured_variables.WORKHOURS_DICTIONARY["dinner_end"]) + "h."}
	else:
		return [True]

def identify_valid_date(input_date):

	"""
	Identify whether the client inputted a valid date
	"""
	import datetime
	try:
	    booking_date = datetime.datetime(year = input_date["year"], month = input_date["month"], day = input_date["day"])
	    valid_date = True
	except ValueError:
	    valid_date = False
	
	if valid_date == False:
		return False, {"Error": "The date introduced is not valid, please confirm the year, month and day of your booking."}

	current_date = datetime.datetime.now()
	if booking_date < current_date:
		return False, {"Error": "The date introduced is in the past, please introduce a valid date."}

	return [True]