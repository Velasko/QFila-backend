import json

from datetime import date
from flask_restx import Resource, fields
from sqlalchemy import exc

from .app import ns, session, api
from .scheme import Base, User, FoodCourt, Restaurant, Meal, FoodType, Cart, Item, safe_serialize

try:
	from ..utilities import checkers
	from ..utilities.models.user import *
except ValueError:
	#If running from inside apis folder
	from utilities import checkers
	from utilities.models.user import *

api.add_model(id.name, id)
api.add_model(user.name, user)

api.add_model(meal.name, meal)
api.add_model(restaurant.name, restaurant)
api.add_model(history.name, history)

def get_data(email, phone) -> (str, str):
	"""Gets email and phone.
	Returns a tuple with the first item being the data and the second
	the field name.
	"""
	if not email is None:
		field = User.email 
		data = email
	elif not phone is None:
		data = phone
		field = User.phone
	else:
		raise KeyError("No argument parsed")
	return data, field

@ns.route('/user')
class UserHandler(Resource):

	@ns.doc("Create user")
	@ns.expect(user)
	@ns.response(201, "Method executed successfully.")
	@ns.response(400, "Invalid payload; missing the required argument in 'missing' field of return")
	@ns.response(403, "Birthday is less than 12 years ago.")
	@ns.response(409, "Email or phone already used.")
	def post(self):
		"""Method to create the user.
		"""
		data = api.payload

		try:
			#checking obligatory fields and modifying as required.
			data['birthday'] = date.fromisoformat(data['birthday'])
			if not checkers.age_check(data['birthday']):
				return {'message' : "User below 12 years old"}, 403

			data['name'] = data['name'].lower()
			data['email'] = data['email'].lower()

			if not checkers.valid_email(data['email']):
				api.abort(400, "Invalid email.")

			data['passwd']

			user = User(**data)
			session.add(user)

			session.commit()
		except (exc.InvalidRequestError, exc.IntegrityError) as e:
			#I don't get why they seem to change between the two.
			session.rollback()
			api.abort(409, e._message().split(".")[-1][:-3] + " already in use.")
		except KeyError as e:
			"Required value is missing"
			session.rollback()
			return {'missing' : e.args[0]}, 400

		return {}, 201

@ns.route('/user/phone/<string:phone>')
@ns.route('/user/email/<string:email>')
class UserHandler_UrlParse(Resource):

	@ns.doc("Find and return user based on phone or email")
	@ns.response(200, "Method executed successfully.", model=user)
	@ns.response(404, "User not found.")
	def get(self, email=None, phone=None):
		"""Method to get user information based on e-mail or phone.
		A single user shall be returned from this query."""

		try:
			data, field = get_data(email, phone)
			query = session.query(User).filter(field == data)
			user = query.first().serialize()

			#hiding user id
			del user['id']

			return user
		except AttributeError:
			return {'message' : 'User not found.'}, 404

	@ns.doc("Modify user")
	@ns.expect(user)
	@ns.response(200, "Method executed successfully.")
	@ns.response(400, "Query invalid.")
	@ns.response(403, "Birthday is less than 12 years ago.")
	@ns.response(404, "User not found.")
	@ns.response(409, "Email or phone already used.")
	def put(self, email=None, phone=None):
		"""Method to modify an user.

		The user identification must be parsed by the url, using either phone or email.
		The fields to be updated must be parsed on the payload.
		"""
		try:
			data, field = get_data(email, phone)
			update = api.payload

			if 'birthday' in update:
				update['birthday'] = date.fromisoformat(update['birthday'])
				if not checkers.age_check(update['birthday']):
					return {'message' : "User below 12 years old"}, 403

			if 'email' in update:
				if not checkers.valid_email(update['email']):
					return {'message' : "Invalid email."}, 400

			query = session.query(User).filter(field == data)
			if query.count() == 0:
				return {'message' : 'No user with such id'}, 404
			query.update(update)
			session.commit()
			return {}, 200
		except KeyError as e:
			session.rollback()
			return {'message' : e.args[0]}, 400
		except exc.IntegrityError as e:
			session.rollback()
			return {'message' : e._message().split(".")[-1][:-3] + " already in use."}, 409
		except Exception:
			session.rollback()
			api.abort(500)

	@ns.doc("Delete user")
	@ns.response(200, "Method executed successfully.")
	@ns.response(404, "User not found.")
	def delete(self, email=None, phone=None):
		"""Method called to delete the user.

		In this scenario, it was prefered to clear out the fields and turn it into
		a ghost user instead. (maybe -> Must verify with protection of data law)

		So far, the user is indeed deleted, if there is no history attached to it.
		"""

		try:
			data, field = get_data(email, phone)

			query = session.query(User).filter(field == data)
			if query.count() == 0:
				return {'message' : 'No user with such id'}, 404
			query.delete()
			session.commit()
			return {}, 200
		except Exception as e:
			session.rollback()
			return {'message' : e.args[0]}, 500

@ns.route('/user/recents/<string:query_mode>/phone/<string:phone>')
@ns.route('/user/recents/<string:query_mode>/email/<string:email>')
class UserRecentsHandler(Resource):

	@ns.doc("Get user's recent meals or restaurants", params={'query_mode' : "Query mode must be 'meals' or 'restaurants'"})
	@ns.response(200, "Method executed successfully.", model=history)
	@ns.response(400, "Invalid payload")
	@ns.response(404, "Query type isn't neiter 'meals' nor 'restaurants'/invalid url")
	def get(self, query_mode, email=None, phone=None):
		"""Returns user recent meals/restaurants
		"""
		invalid_payload = {'message' : 'Invalid payload.'}
		try:
			data, field = get_data(email, phone)
		except KeyError:
			return invalid_payload, 400
		else:
			if session.query(User).filter(field == data).count() == 0:
				return invalid_payload, 400

		if query_mode == 'meals':
			initial_query = session.query(
					Meal
				).join(
					Item,
					Item.rest == Meal.rest and \
					Item.meal == Meal.id
				)
		elif query_mode == 'restaurants':
			initial_query = session.query(
					Restaurant
				).join(
					Item,
					Item.rest == Restaurant.id
				)
		else:
			api.abort(404)

		query = initial_query.join(
			User,
			User.id == Item.user
		).filter(
			field == data
		).order_by(
			Item.time.desc()
		# ).distinct(
		# 	# Restaurant
		).limit(3)

		return {query_mode : [safe_serialize(rest) for rest in query.all()]}, 200