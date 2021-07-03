from ..app import DBsession

from sqlalchemy import exc

from ..scheme import *

try:
	from ...utilities import checkers
except ValueError:
	#If running from inside apis folder
	from utilities import checkers

def fetch_user(user_type, key, value):
	with DBsession as session:
			query = session.query(user_type).filter(
				getattr(user_type, key) == value
			)

			if query.count() == 0:
				return {'message' : 'Restaurant not found'}, 404

			return query.first().serialize()

def update_user(user_type, key, value, update_data):
	if 'id' in update_data:
		del update_data['id']

	with DBsession as session:
		try:
			login_data = {}

			if 'email' in update_data:
				if not checkers.valid_email(update_data['email']):
					return {'message' : "Invalid email."}, 400

				login_data['email'] = update_data['email']
				del update_data['email']

			if 'phone' in update_data:
				login_data['phone'] = update_data['phone']
				del update_data['phone']

			login = session.query(Login).filter(
				getattr(Login, key) == value
			)

			if login.count() == 0:
				return {'message' : 'No client with such id'}, 404

			user = session.query(user_type).filter(
				user_type.id == login.first().id
			)

			if login_data != {}:
				login.update(login_data)

			if update_data != {}:
				user.update(update_data)

			session.commit()
			return {'message' : 'update sucessfull'}, 200
		except (KeyError, exc.InvalidRequestError) as e:
			return {'message' : 'invalid payload'}, 400
		except exc.IntegrityError as e:
			return {'message' : e._message().split(".")[-1][:-3] + " already in use."}, 409