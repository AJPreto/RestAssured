#!/usr/bin/env python

"""
RestAssured variables that can be changed to customize restaurant data
"""

__author__ = "A.J. Preto"
__email__ = "martinsgomes.jose@gmail.com"
__project__ = "RestAssured - Restaurant challenge"
MAX_TABLES = 10
WORKHOURS_DICTIONARY = {"lunch_start": 12, "lunch_end": 15, "dinner_start": 19, "dinner_end": 23}
WORKING_HOURS_INTERVALS = list(range(WORKHOURS_DICTIONARY["lunch_start"], WORKHOURS_DICTIONARY["lunch_end"] + 1, 1)) + \
							list(range(WORKHOURS_DICTIONARY["dinner_start"], WORKHOURS_DICTIONARY["dinner_end"] + 1,1))
BUSY_STATUS = ["prepping", "cooking", "ready"]
