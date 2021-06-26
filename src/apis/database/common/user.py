from ..app import DBsession

from sqlalchemy import exc

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
			if 'email' in update_data:
				if not checkers.valid_email(update_data['email']):
					return {'message' : "Invalid email."}, 400

			query = session.query(user_type).filter(
				getattr(user_type, key) == value
			)

			if query.count() == 0:
				return {'message' : 'No client with such id'}, 404
			query.update(update_data)
			session.commit()
			return {'message' : 'update sucessfull'}, 200
		except (KeyError, exc.InvalidRequestError) as e:
			return {'message' : 'invalid payload'}, 400
		except exc.IntegrityError as e:
			return {'message' : e._message().split(".")[-1][:-3] + " already in use."}, 409