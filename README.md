# RestAssured

A FastAPI booking system for restaurants.

## Developed with:
- Python 3.11.0
- FastAPI
- SQL

## Dependencies Installation:
- pip install fastapi uvicorn sqlite3

## Running:
- uvicorn [script_name]:app --reload 

## Documentation:
- localhost/docs

## Scripts:
- RestAssured_database.py - Creates the SQL database, needs to be run once, before launching the App.
- RestAssured_App.py - Launches the FastAPI framework
- RestAssured_variables.py - restaurant-dependent variables such as working hours
- RestAssured_booking.py - functions useful for the "booking" section
- RestAssured_orders.py - functions useful for the "orders" section
- RestAssured_menu.py - functions useful for the "menu" section

# Endpoints
- Home - "/" - simple introduction to the software

- Documentation - "/docs" - FastAPI automatically generated interactive display of all the endpoints

- Booking - "/booking/" - when adding the input_date afterwards, it attempts to book a reservation, and outputs the reserved table
 - input_date

- Update Booking - "/update-booking/" - allows the update of a previously booked reservation, by first inserting the new one and later delete the previous
 - input_old_date
 - input_old_table_number
 - input_new_date
 - input_new_table_number 

- Cancel Booking - "/cancel-booking/" - allows the cancellation of a previously booked reservation
 - input_old_date
 - input_old_table_number

- Booking overview - "/booking-overview/" - show all the booked reservations

- Table availability - "/table-availability/" - shows the available tables for a given date
 - input_date
 - input_table_number 

- Extend Menu - "/extend-menu/" - add new products to the menu, with respective prices
 - input_product
 - input_price

- Update Menu - "/update-menu/" - update an entry in the menu
 - input_product
 - input-price

- Remove Menu - "/remove-menu/" - remove an entry from the menu
 - input_product

- Menu Overview - "/menu-overview/" - displays the whole menu

- New Order - "/new-order/" - allows the ordering of products for a table
 - input_products
 - input_table

- Update Order Cooking - "/update-order-cooking/" - updates the order to cooking status
 - input_table

- Update Order Ready - "/update-order-ready/" - updates the order to ready status
 - input_table

- Update Order paid - "/update-order-paid/" - updates the order to cooking status
 - input_table

- Orders Overview - "/orders-overview/" - shows the order, depending on order motif
 - order_motif