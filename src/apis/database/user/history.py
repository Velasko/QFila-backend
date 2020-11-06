import json

from datetime import date
from flask_restx import Resource, fields
from sqlalchemy import exc

from ..app import ns, session, api
from ..scheme import Base, User, FoodCourt, Restaurant, Meal, FoodType, Cart, Item, safe_serialize

try:
	from ...utilities import checkers
	from ...utilities.models.user import *
except ValueError:
	#If running from inside apis folder
	from utilities import checkers
	from utilities.models.user import *

for model in (meal, restaurant, history):
	api.add_model(model.name, model)

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