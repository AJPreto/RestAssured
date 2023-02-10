#!/usr/bin/env python

"""
Initialize the database, should be run to generate the empty database
"""

__author__ = "A.J. Preto"
__email__ = "martinsgomes.jose@gmail.com"
__project__ = "RestAssured - Restaurant challenge"

import sqlite3
"""
Initialize the database
"""
database_connection = sqlite3.connect('RestAssured')
sql_cursor = database_connection.cursor()

"""
Create menu table with columns:
- product_id
- product_name
- price
"""
sql_cursor.execute('''
          CREATE TABLE IF NOT EXISTS menu
          (product_id INTEGER PRIMARY KEY, product_name TEXT, price REAL);
          ''')


"""
Create bookings table with columns:
- booking_id
- table_id
- year
- month
- day
- hour
"""          
sql_cursor.execute('''
          CREATE TABLE IF NOT EXISTS bookings
          (booking_id INTEGER PRIMARY KEY, table_id INTEGER, year INTEGER, month INTEGER, day INTEGER, hour INTEGER) 
          ''')

"""
Create orders table with columns:
- order_id
- table_id
- product_list_string
- order_status
- full_price
- start_time
- end_time
- tip
"""   
sql_cursor.execute('''
          CREATE TABLE IF NOT EXISTS orders
          (order_id INTEGER PRIMARY KEY, table_id INTEGER, product_list_string TEXT, order_status TEXT, full_price REAL, start_time TIMESTAMP, end_time TIMESTAMP, tip REAL) 
          ''')
                     
database_connection.commit()
sql_cursor.close()