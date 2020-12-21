import os
import time
import unittest

from datetime import date
from requests import put, get, post, delete

from .scheme import Base, User, Restaurant, Meal, FoodType, Cart, Item

hostname = "http://localhost:5000/database/user"
default_data = {"name" : "test user", "birthday" : "1977-01-01", "email" : "test@database.qfila", "passwd":3, 'phone':200000000}


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DATABASE_ENGINE = os.getenv('DATABASE_ENGINE')
# engine = create_engine(DATABASE_ENGINE)
# Base.metadata.bind = engine
# DBSession = sessionmaker(bind=engine)
# database = DBSession()
from .app import session as database


headers = {
	"accept": "application/json",
	"Content-Type": "application/json"
}

class DatabaseUserTest(unittest.TestCase):

	def clean_delete_user(self, email):
		"""Method to clean the done test"""
		query = database.query(User).filter(User.email==email)

		query.delete()
		database.commit()

	def d_test_post_user_obligatory_keys(self):
		"""Tests if the fields name, birthday, email and password are required for the user creation."""

		data = default_data.copy()

		#testing if the those keys are obligatory when creating an user
		for obligatory in ('name', 'birthday', 'email', 'passwd'):
			with self.subTest(obligatory=obligatory):
				resp = post(hostname, data={ key : value for key, value in data.items() if key != obligatory})
				self.assertEqual(resp.status_code, 400)
				self.assertEqual(resp.json()['message'], obligatory)

	def d_test_post_user_field_validation(self):
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

	def test_post_user_creation(self):
		"""Testing insert of user and it's unicity"""

		data = default_data.copy()
		# data['email'] = 'potato@gmail.com'
		# data['phone'] = 23
		resp = post(hostname, data=data, headers=headers).status_code

		self.assertEqual(resp, 201)

		data['phone'] = data['phone']*2
		resp = post(hostname, data=data, headers=headers)
		self.assertEqual(resp.status_code, 409)

		data['phone'] = default_data['phone']
		data['email'] = data['email'] + '2'
		resp = post(hostname, data=data, headers=headers)
		self.assertEqual(resp.status_code, 409)

		self.clean_delete_user(data['email'][:-1])


	def u_test_get_user(self):
		"""Testing to retrieve user"""
		pass
#		resp = get(hostname, )

	def u_test_put_user(self):
		"""Testing to modify user"""
		pass

	def u_test_delete_user(self):
		"""Testing to delete user"""
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