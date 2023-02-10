#!/usr/bin/env python

"""
Variables to be used to for the orders section of RestAssured API 
"""

__author__ = "A.J. Preto"
__email__ = "martinsgomes.jose@gmail.com"
__project__ = "RestAssured - Restaurant challenge"

import RestAssured_variables

def menu_access_and_price(input_connection, products_list):

	"""
	Identify if the items on the order are in the menu.
	Return the full bill for an order
	Output: (menu_status, order_connection, message, bill)
	"""
	full_bill, failed_products = 0, []
	for entry in products_list:
		try:
			menu_entry = list(input_connection.execute("SELECT * FROM menu WHERE product_name=?", (entry,)))
			full_bill += float(menu_entry[0][2])
		except:
			failed_products.append(entry)

	if len(failed_products) > 0:
		return False, input_connection, {"Error": "Some of the products (" + ",".join(failed_products) + \
				 ") you selected are not on the menu, please confirm your order."}, full_bill
	elif len(failed_products) == 0:
		return True, input_connection, {"Success": "All the items you input are on the menu."}, full_bill

def confirm_table_busy(input_connection, input_table_number, update_mode = False):

	"""
	Check if the input table has any ongoing orders, in order to avoid duplicates
	update_mode retrieves the data of the ongoing order, to be used for update
	"""
	table_orders = input_connection.execute("SELECT * FROM orders WHERE table_id=?", (input_table_number,))
	proceed_status = True
	for row in list(table_orders):
		if row[3] in RestAssured_variables.BUSY_STATUS:
			proceed_status = False
			return row, proceed_status, input_connection
	return [], proceed_status, input_connection

def update_order_status(input_connection, input_table_number, order_list, \
				status_string = "", input_tip = None, meal_finish = None):

	"""
	Update order status, to be used for "cooking" and "ready" status
	"""
	input_connection.execute("INSERT INTO orders (table_id, product_list_string, order_status, full_price, start_time, end_time, tip) \
      				VALUES (?, ?, ?, ?, ?, ?, ?)", (input_table_number, order_list[2], status_string, order_list[4], order_list[5], meal_finish, input_tip))
	input_connection.execute("DELETE FROM orders WHERE order_id=?", \
						(order_list[0],))
	return input_connection

