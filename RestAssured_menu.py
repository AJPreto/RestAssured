#!/usr/bin/env python

"""
Variables to be used to for the booking section of RestAssured API 
"""

__author__ = "A.J. Preto"
__email__ = "martinsgomes.jose@gmail.com"
__project__ = "RestAssured - Restaurant challenge"

import RestAssured_variables

def menu_overlapping(input_connection, input_product, input_price, only_duplicates = True):

	"""
	Check if the input product is already on the list and, if yes, if it has the same price has before
	- "only_duplicates" mode is designed for input values only, if False, if will give different messages depending on price
	Output: (duplicate_status, sql_connection, message, [old_price: if only_duplicates is False])
	"""
	duplicate_products = input_connection.execute("SELECT * FROM menu WHERE product_name=?",\
				 (input_product,))
	duplicate_products_list = list(duplicate_products)

	if len(duplicate_products_list) == 0:
		if only_duplicates == True:
			return False, input_connection, {"Success": "There is no entry for " + input_product + " with price " + str(input_price) + "."}

		return False, input_connection, {"Error": "There was no previous entry for " + input_product + "."}, ""

	if len(duplicate_products_list) > 0:

		if only_duplicates == True:
			return True, input_connection, {"Error": "There is already an entry for " + input_product + "."}

		different_previous_price, old_price = True, 0
		for row in duplicate_products_list:
			old_price = row[2]
			if row[2] == input_price:
				different_previous_price = False

		if different_previous_price == False:
			return True, input_connection, {"Error": "There is already an entry for " + input_product + " with price " + str(input_price) + "."}, old_price

		elif different_previous_price == True:
			return True, input_connection, {"Success": "There is already an entry for " + input_product + " however, the price is different."}, old_price