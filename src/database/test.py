import os
import time
import unittest

from datetime import date
from requests import put, get, post, delete

hostname = f"{os.getenv('APPLICATION_HOSTNAME')}/database/user"
default_data = {"name" : "test user", "birthday" : "1977-01-01", "email" : "test@database.qfila", "passwd":3, 'phone':85900000000}


class DatabaseUserTest(unittest.TestCase):

	def test_post_user_obligatory_keys(self):
		"""Tests if the fields name, birthday, email and password are required for the user creation."""

		data = default_data.copy()

		#testing if the those keys are obligatory when creating an user
		for obligatory in ('name', 'birthday', 'email', 'passwd'):
			resp = post(hostname, data={ key : value for key, value in data.items() if key != obligatory})
			self.assertEqual(resp.status_code, 400)
			self.assertEqual(resp.json()['message'], obligatory)
			print('')

	def test_post_user_field_validation(self):
		'''Test to check if the values for each field is valid.'''

	#tests for the name field

	#tests for the birthday field
		#minimum age test
		tdy = date.today()
		almost_twelve_years_ago = date(tdy.year-12, tdy.month, tdy.day+1)
		data = default_data.copy()
		data['birthday'] = almost_twelve_years_ago.isoformat()
		resp = post(hostname, data=data)

		self.assertEqual(resp.status_code, 403)
		self.assertEqual(resp.json()['message'], 'User below 12 years old')


	#tests for the email field


	#tests for the phone field

	def test_post_user_creation_unicity(self):
		data = default_data.copy()
		resp = post(hostname, data=data)
		print(resp)

		resp = post(hostname, data=data)
		self.assertEqual(resp.status_code, 409)


	def test_get_user(self):
		pass
#		resp = get(hostname, )

	def test_put_user(self):
		pass

	def test_delete_user(self):
		pass

def execute_tests(*args, **kwargs):
	time.sleep(3)

	unittest.main(*args, **kwargs)

	time.sleep(3)

if __name__ == '__main__':
	unittest.main()
#put
#curl http://localhost:5000/database/user -d 'data={"id": {"email": "gmail"}, "update": {"birthday": "1997-04-30"}}' -X PUT

#delete
#curl http://localhost:5000/database/user -d "email=gmail" -X DELETE

#get
#curl http://localhost:5000/database/user -d "email=gmail" -X GET