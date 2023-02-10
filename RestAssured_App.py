#!/usr/bin/env python

"""
Installation:
- pip install fastapi uvicorn sqlite3
Running:
- uvicorn [script_name]:app --reload 
Documentation:
- localhost/docs
"""

__author__ = "A.J. Preto"
__email__ = "martinsgomes.jose@gmail.com"
__project__ = "RestAssured - Restaurant challenge"

import fastapi
from fastapi import FastAPI, Path, Query, HTTPException, status
import sys
import sqlite3
from typing import Optional
import RestAssured_variables
import RestAssured_booking
import RestAssured_menu
import RestAssured_orders

"""
Initialize the API
"""

app = FastAPI()
@app.get("/")
def root():
	return {"Success": "Welcome to RestAssured, your FastAPI to manage restaurant reservations, menu and orders. Please add '/docs' for a more interactive view."}

@app.post("/booking/{input_date}/")
def booking(input_date: Optional[str] = Query(description = "The date of the reservation (YYYY-MM-DD-HH)"), \
				input_table_number: Optional[str] = None):

	date = RestAssured_booking.split_date(input_date)

	"""
	Check if booking hour is in workhours 
	"""
	check_work_hours = RestAssured_booking.assess_work_hours(date["hour"])
	if check_work_hours[0] == False:
		return check_work_hours[1]

	"""
	Check if the date is valid and whether the customer is attempting to book a date in the past
	"""
	check_date = RestAssured_booking.identify_valid_date(date)
	if check_date[0] == False:
		return check_date[1]

	"""
	Check whether the table exists
	"""
	if (input_table_number != None) and (int(input_table_number) not in range(1, RestAssured_variables.MAX_TABLES + 1)):
		return {"Error": "It is not possible to choose that table, please attempt a table number between 1 and " + str(RestAssured_variables.MAX_TABLES)}

	booking_connection = sqlite3.connect('RestAssured', check_same_thread = False)
	simultaneous_reservations_list, occupied_tables, unoccupied_tables, booking_connection = RestAssured_booking.booking_overlapping(booking_connection, date)

	if (input_table_number != None) and (int(input_table_number) not in occupied_tables):
		
		"""
		Register booking when customer picks a table not being used yet at his date
		"""
		booking_connection = RestAssured_booking.insert_booking(booking_connection, input_table_number, date)
		booking_connection.commit()
		booking_connection.close()
		return {"Success": "Your reservation was successfully booked for " + input_date + \
				", as well as for your table of choice - " + str(input_table_number) + \
				". Please remember this information in case you need to rebook your visit."}

	elif (input_table_number != None) and (int(input_table_number) in occupied_tables):

		"""
		Warn customer he customer picked a table already being used at his date and time
		"""
		booking_connection.close()
		return {"Error:" "The table you chose has already been picked by another customer, at that date and time, other available tables are:" + \
			", ".join([str(vaccant_table) for vaccant_table in unoccupied_tables]) + "."}

	if (input_table_number == None) and (len(unoccupied_tables) != 0):
		booking_connection = RestAssured_booking.insert_booking(booking_connection, unoccupied_tables[0], date)
		booking_connection.commit()
		booking_connection.close()
		return {"Success": "Your reservation was successfully booked for " + input_date + \
				", as well as for table " + str(unoccupied_tables[0]) + \
				". Please remember this information in case you need to rebook your visit"}

	if (input_table_number == None) and (len(unoccupied_tables) == 0):
		booking_connection.close()
		return {"Error": "Your reservation could be booked for that date and hour, since all the tables are occupied."}

@app.put("/update-booking/{input_old_date}/{input_old_table_number}/{input_new_date}/{input_new_table_number}")
def update_booking(input_old_date: Optional[str] = Query(description = "The date of the previous reservation (YYYY-MM-DD-HH)"), \
				input_old_table_number: Optional[str] = None, \
				input_new_date: Optional[str] = Query(description = "The date of the new reservation (YYYY-MM-DD-HH)"), \
				input_new_table_number: Optional[str] = None):

	old_date = RestAssured_booking.split_date(input_old_date)
	new_date = RestAssured_booking.split_date(input_new_date)

	"""
	Check if the date is valid and whether the customer is attempting to book a date in the past
	"""
	check_work_hours = RestAssured_booking.assess_work_hours(new_date["hour"])
	if check_work_hours[0] == False:
		return check_work_hours[1]

	"""
	Check whether the table exists
	"""
	if (input_new_table_number != None) and (int(input_new_table_number) not in range(1, RestAssured_variables.MAX_TABLES + 1)):
		return {"Error": "It is not possible to choose that table, please attempt a table number between 1 and " + str(RestAssured_variables.MAX_TABLES)}

	booking_connection = sqlite3.connect('RestAssured', check_same_thread = False)

	"""
	Check whether the customer input information about the old information is true
	"""
	booking_connection, old_status = RestAssured_booking.booking_overlapping(booking_connection, old_date, \
				check_mode = True, input_table_number = input_old_table_number)
	if old_status == False:
		booking_connection.close()
		return {"Error": "There was no reservation booked for " + input_old_date + \
				", table " + str(input_old_table_number) + ", please confirm your prior reservation before proceeding with the booking update."}

	"""
	Check whether the new information allows for the customer's booking
	"""
	simultaneous_reservations_list, occupied_tables, unoccupied_tables, booking_connection = RestAssured_booking.booking_overlapping(booking_connection, new_date)

	if (input_new_table_number != None) and (int(input_new_table_number) not in occupied_tables):
		
		"""
		Register booking when customer picks a table not being used yet at his date
		"""
		booking_connection = RestAssured_booking.insert_booking(booking_connection, input_new_table_number, new_date)
		booking_connection = RestAssured_booking.delete_booking(booking_connection, input_old_table_number, old_date)
		booking_connection.commit()
		booking_connection.close()
		return {"Success": "Your reservation was successfully booked for " + input_new_date + \
				", as well as for your table of choice " + str(input_new_table_number) + \
				". Please remember this information in case you need to rebook your visit."}

	elif (input_new_table_number != None) and (int(input_new_table_number) in occupied_tables):

		"""
		Warn customer he customer picked a table already being used at his date and time
		"""
		booking_connection.close()
		return {"Error:" "The table you chose has already been picked by another customer, at that date and time, other available tables are:" + \
			", ".join([str(vaccant_table) for vaccant_table in unoccupied_tables]) + "."}

	if (input_new_table_number == None) and (len(unoccupied_tables) != 0):
		booking_connection = RestAssured_booking.insert_booking(booking_connection, unoccupied_tables[0], new_date)
		booking_connection = RestAssured_booking.delete_booking(booking_connection, input_old_table_number, old_date)
		booking_connection.commit()
		booking_connection.close()
		return {"Success": "Your reservation was successfully booked for " + input_new_date + \
				", as well as for table " + str(unoccupied_tables[0]) + \
				". Please remember this information in case you need to rebook your visit"}

	if (input_new_table_number == None) and (len(unoccupied_tables) == 0):
		booking_connection.close()
		return {"Error": "Your reservation could be booked for that date and hour, since all the tables are occupied."}

@app.delete("/cancel-booking/{input_old_date}/{input_old_table_number}")
def cancel_booking(input_old_date: Optional[str] = Query(description = "The date of the previous reservation (YYYY-MM-DD-HH)"), \
				input_old_table_number: Optional[str] = None):

	old_date = RestAssured_booking.split_date(input_old_date)
	booking_connection = sqlite3.connect('RestAssured', check_same_thread = False)

	"""
	Check whether the customer input information about the old information is true
	"""
	booking_connection, old_status = RestAssured_booking.booking_overlapping(booking_connection, old_date, \
				check_mode = True, input_table_number = input_old_table_number)
	if old_status == False:
		booking_connection.close()
		return {"Error": "There was no reservation booked for " + input_old_date + \
				", table " + str(input_old_table_number) + \
				", please confirm your prior reservation to conclude your booking cancellation."}

	RestAssured_booking.delete_booking(booking_connection, input_old_table_number, old_date)
	booking_connection.commit()
	booking_connection.close()
	return {"Success": "Your reservation was successfully cancelled for " + input_old_date + " ."}

@app.get("/booking-overview/")
def booking_overview():

	"""
	Display all the booked reservations, in descendent order by year, month, day and hour, respectively
	"""
	booking_connection = sqlite3.connect('RestAssured', check_same_thread = False)
	all_reservations = booking_connection.execute("SELECT * FROM bookings ORDER BY year DESC, month DESC, day DESC, hour DESC")
	reservations_list = []
	for row in all_reservations:
		reservations_list.append({"table_id": row[1], "year": row[2], \
		"month": row[3], "day": row[4], "hour": row[5]})
	booking_connection.commit()
	booking_connection.close()
	return {"Success": reservations_list}

@app.get("/table-availability/{input_date}/{input_table_number}")
def table_availability(input_date: Optional[str] = Query(description = "The date to check for table availability (YYYY-MM-DD-HH)"), \
						input_table_number: Optional[str] = None):
	
	"""
	Check whether there are available tables for an input date
	"""
	booking_connection = sqlite3.connect('RestAssured', check_same_thread = False)

	date = RestAssured_booking.split_date(input_date)

	"""
	Check if the date is valid and whether the customer is attempting to book a date in the past
	"""
	check_work_hours = RestAssured_booking.assess_work_hours(date["hour"])
	if check_work_hours[0] == False:
		booking_connection.close()
		return check_work_hours[1]

	"""
	Check whether the table exists
	"""
	if (input_table_number != None) and (int(input_table_number) not in range(1, RestAssured_variables.MAX_TABLES + 1)):
		booking_connection.close()
		return {"Error": "It is not possible to choose that table, please attempt a table number between 1 and " + str(RestAssured_variables.MAX_TABLES)}

	simultaneous_reservations_list, occupied_tables, unoccupied_tables, booking_connection = RestAssured_booking.booking_overlapping(booking_connection, date)
	booking_connection.commit()
	booking_connection.close()

	if len(occupied_tables) == 0:
		return {"Success": "There are no occupied tables for " + input_date + "."}

	elif (len(occupied_tables) > 0) and (len(unoccupied_tables) > 0):
		return {"Success": "There are some occupied tables for " + input_date + ". " + \
				"However, tables " + ", ".join([str(vaccant_table) for vaccant_table in unoccupied_tables]) +  " are free." }

	elif (len(unoccupied_tables) == 0):
		return {"Error": "There are no free tables for " + input_date + "."}

@app.post("/extend-menu/{input_product}/{input_price}")
def extend_menu(input_product: Optional[str] = Query(description = "Insert the product name"), \
				input_price: Optional[float] = Query(description = "Insert the product price")):
	
	"""
	Add a new entry to the menu
	"""
	menu_connection = sqlite3.connect('RestAssured', check_same_thread = False)
	overlap_status, menu_connection, message = RestAssured_menu.menu_overlapping(menu_connection, input_product, input_price)

	if overlap_status == True:
		menu_connection.close()
		return message

	menu_connection.execute("INSERT INTO menu (product_name, price) \
      				VALUES (?, ?)", (input_product, input_price))
	menu_connection.commit()
	menu_connection.close()
	return {"Success": "Your product " + input_product + \
				" was added to the menu, with price " + str(input_price) + "."}

@app.put("/update-menu/{input_product}/{input_price}")
def update_menu(input_product: Optional[str] = Query(description = "Insert the product name"), \
				input_price: Optional[float] = Query(description = "Insert the product price")):
	
	"""
	Add a new entry to the menu
	"""
	menu_connection = sqlite3.connect('RestAssured', check_same_thread = False)
	overlap_status, menu_connection, message, old_price = RestAssured_menu.menu_overlapping(menu_connection, \
			input_product, input_price, only_duplicates = False) #only_duplicates turn to False in case the intent is simply to change the price
	
	if overlap_status == True:
		if list(message.keys())[0] == "Error":
			menu_connection.close()
			return message

	menu_connection.execute("INSERT INTO menu (product_name, price) \
      				VALUES (?, ?)", (input_product, input_price))
	menu_connection.execute("DELETE FROM menu WHERE product_name=? AND price=?", \
						(input_product, old_price))
	menu_connection.commit()
	menu_connection.close()
	return {"Success": "Your product " + input_product + \
				" was updated, with the new price " + str(input_price) + "."}	

@app.delete("/remove-menu/{input_product}")
def remove_menu(input_product: Optional[str] = Query(description = "Insert the product name")):
	
	"""
	Delete an entry from the menu
	"""
	menu_connection = sqlite3.connect('RestAssured', check_same_thread = False)
	overlap_status, menu_connection, message = RestAssured_menu.menu_overlapping(menu_connection, \
			input_product, "") #only_duplicates turn to False in case the intent is simply to change the price
	
	if overlap_status == False:
		menu_connection.close()
		return {"Error": "There is no product with name " + input_product + "."}

	if overlap_status == True:
		menu_connection.execute("DELETE FROM menu WHERE product_name=?", \
					(input_product,))

	menu_connection.commit()
	menu_connection.close()
	return {"Success": "Your product " + input_product + \
				" was successfully was deleted."}	

@app.get("/menu-overview/")
def menu_overview():

	"""
	Display the menu
	"""
	menu_connection = sqlite3.connect('RestAssured', check_same_thread = False)
	full_menu = menu_connection.execute("SELECT * FROM menu")
	full_menu_list = []
	for row in full_menu:
		full_menu_list.append({"product_name": row[1], "price": row[2]})
	menu_connection.commit()
	menu_connection.close()
	return {"Success": full_menu_list}

@app.post("/new-order/{input_products}/{input_table}")
def new_order(input_products: Optional[str] = Query(description = "Insert the product names, separated by commas"), \
				input_table: Optional[int] = Query(description = "Insert the table to which this order is associated")):
	
	"""
	Add a new entry to the menu.
	table_order_status will prevent duplicate orders
	menu_status will prevent collecting orders with items not on the menu
	"""
	input_products_list = input_products.replace(" ","").split(",")
	order_connection = sqlite3.connect('RestAssured', check_same_thread = False)

	dummy_row, table_order_status, order_connection = RestAssured_orders.confirm_table_busy(order_connection, input_table)
	if table_order_status == False:
		order_connection.close()
		return {"Error": "It is not possible to register another order for table " + str(input_table) + ", please confirm the table number."}

	menu_status, order_connection, message, bill = RestAssured_orders.menu_access_and_price(order_connection, input_products_list)
	if menu_status == False:
		order_connection.close()
		return message

	"""
	Add the order to the log, registering the total bill, and the time of the order
	"""
	import datetime
	current_time = datetime.datetime.now()
	order_connection.execute("INSERT INTO orders (table_id, product_list_string, order_status, full_price, start_time, end_time, tip) \
      				VALUES (?, ?, ?, ?, ?, ?, ?)", (input_table, input_products, "prepping", bill, current_time , None, None))

	order_connection.commit()
	order_connection.close()
	return {"Success": "Your order has been registered, for the items " + input_products + "."}

@app.put("/update-order-cooking/{input_table}")
def update_order_cooking(input_table: Optional[int] = Query(description = "Insert the table whose order is now cooking")):
	
	"""
	Update the ongoing from from a table to "cooking" status
	"""
	order_connection = sqlite3.connect('RestAssured', check_same_thread = False)

	current_table_order, table_order_status, order_connection = RestAssured_orders.confirm_table_busy(order_connection, input_table)
	if table_order_status == True:
		order_connection.close()
		return {"Error": "It is not possible to update the order for table " + str(input_table) + ", since it has no ongoing orders."}

	if current_table_order[3] in ["cooking", "ready"]:
		return {"Error": "It is not possible to update the order from table " + str(input_table) + \
			" to cooking, since it already has " + current_table_order[3] + " status."}

	order_connection = RestAssured_orders.update_order_status(order_connection, input_table, current_table_order, status_string = "cooking")
	order_connection.commit()
	order_connection.close()
	return {"Success": "Your order from table " + str(input_table) + " has been updated to cooking."}

@app.put("/update-order-ready/{input_table}")
def update_order_ready(input_table: Optional[int] = Query(description = "Insert the table whose order is now ready")):
	
	"""
	Update the ongoing from from a table to "cooking" status
	"""
	order_connection = sqlite3.connect('RestAssured', check_same_thread = False)

	current_table_order, table_order_status, order_connection = RestAssured_orders.confirm_table_busy(order_connection, input_table)
	if table_order_status == True:
		order_connection.close()
		return {"Error": "It is not possible to update the order for table " + str(input_table) + ", since it has no ongoing orders."}

	if current_table_order[3] in ["prepping", "ready"]:
		return {"Error": "It is not possible to update the order from table " + str(input_table) + \
			" to ready, since it has " + current_table_order[3] + " status."}

	order_connection = RestAssured_orders.update_order_status(order_connection, input_table, current_table_order, status_string = "ready")
	order_connection.commit()
	order_connection.close()
	return {"Success": "Your order from table " + str(input_table) + " has been updated to ready."}

@app.put("/update-order-paid/{input_table}")
def update_order_paid(input_table: Optional[int] = Query(description = "Insert the table whose order is now paid"), \
						input_tip_value: Optional[float] = None):
	
	"""
	Update the order status to "paid", registers the tip, if there is one
	"""
	order_connection = sqlite3.connect('RestAssured', check_same_thread = False)

	current_table_order, table_order_status, order_connection = RestAssured_orders.confirm_table_busy(order_connection, input_table)
	if table_order_status == True:
		order_connection.close()
		return {"Error": "It is not possible to update the order for table " + str(input_table) + ", since it has no ongoing orders."}

	if current_table_order[3] in ["prepping", "cooking"]:
		return {"Error": "It is not possible to update the order from table " + str(input_table) + \
			" to ready, since it has " + current_table_order[3] + " status."}

	import datetime
	current_time = datetime.datetime.now()
	order_connection = RestAssured_orders.update_order_status(order_connection, input_table, current_table_order, \
		status_string = "paid", input_tip = input_tip_value, meal_finish = current_time)
	order_connection.commit()
	order_connection.close()
	return {"Success": "Your order from table " + str(input_table) + " has been updated to paid."}

@app.get("/orders-overview/{order_motif}")
def orders_overview(order_motif: Optional[str] = "active"):

	"""
	Display the orders. Allows for different two possible settings, default being "active":
	- "active" - sort the active orders (not paid) by descending entry time
	- "all" - sort all the orders by descending entry time

	It is also possible to subset by the available order status:
	- "prepping"
	- "cooking"
	- "ready"
	- "paid"
	"""

	orders_connection = sqlite3.connect('RestAssured', check_same_thread = False)
	if order_motif == "active":
		orders_log = orders_connection.execute("SELECT * FROM orders WHERE order_status!='paid' ORDER BY start_time DESC")

	if order_motif == "all":
		orders_log = orders_connection.execute("SELECT * FROM orders ORDER BY start_time DESC")

	if order_motif in ["prepping", "cooking", "ready", "paid"]:
		orders_log = orders_connection.execute("SELECT * FROM orders WHERE order_status==? ORDER BY start_time DESC", (order_motif,))

	orders_log_list = []
	for row in orders_log:
		orders_log_list.append({"table_number": row[1], "products": row[2], \
							"status": row[3], "bill": row[4], "meal_start": row[5], \
							"meal_end": row[6]})
	orders_connection.commit()
	orders_connection.close()
	return {"Success": orders_log_list}

	
	








	
	
	
	
	
