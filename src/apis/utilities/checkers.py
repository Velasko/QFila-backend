#even though it's a good boardgame, this file 
#have functions to check their inputs as valid ones

import datetime
import re


def age_check(d):
	"""Checks the age based on the date
		
		If it's below 12 years old:
			return False
		Else:
			return True
	"""

	if isinstance(d, str):
		d = datetime.date.fromisoformat(d)

	tdy = datetime.date.today()
	twelve_years_ago = datetime.date(tdy.year-12, tdy.month, tdy.day)

	return d <= twelve_years_ago

def valid_email(email):
	"""Checks if the email follows the required

		If it's valid:
			return True:
		Else:
			Return False
	"""

	match = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)
	return match is not None

def valid_password(password):
	return True