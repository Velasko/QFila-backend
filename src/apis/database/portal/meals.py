from flask_restx import Resource
from sqlalchemy import exc
from sqlalchemy.sql import case

from . import DBsession, ns, api
from ..scheme import *
from ..catalog.common import fetch_meal_complements

try:
	from ...utilities.models.portal import *
	from ...utilities.models.database import meal
except ValueError:
	#If running from inside apis folder
	from utilities.models.portal import *
	from utilities.models.database import meal

for model in (meal, meal_create, meal_edit, meal_list):
	api.add_model(model.name, model)

@ns.route('/meals/fetch/<int:rest>')
class MealFetcher(Resource):

	@ns.doc("Returns the restaurant's meals")
	@ns.expect(meal_list)
	@ns.response(200, "Successfully fetched sections", model=None)
	def post(self, rest):
		with DBsession as session:
			query = session.query(Meal).filter(
				Meal.rest == rest
			)

			if 'meals' in api.payload:
				print("inside if")
				query = query.filter(
					Meal.id.in_(api.payload['meals'])
				)

			response = { 'meal' : [item.serialize() for item in query.all()]}
			fetch_meal_complements(response)

		return response, 200

@ns.route("/meals/<int:rest>")
class MealManager(Resource):

	@ns.doc("Creates a restaurant meal")
	@ns.expect(meal_create)
	@ns.response(200, "Successfully created meal")
	@ns.response(400, "Invalid payload")
	@ns.response(409, "Meal already exists")
	def post(self, rest):
		with DBsession as session:
			try:
				fields = ('description', 'image', 'available')
				meal = Meal(
					rest=rest,
					name=api.payload['name'],
					price=api.payload['price'],
					foodtype=api.payload['foodtype'],
					**{
						f_type : api.payload[f_type]
						for f_type in fields if f_type in api.payload
					}
				)
				session.add(meal)
				session.commit()
				return {'message' : 'Meal created successfully'}, 200
			except KeyError:
				return {'message' : 'Missing arguments in payload'}, 400
			except exc.IntegrityError:
				return {'message' : 'Meal already exists'}, 409

	@ns.doc("Edits a meal")
	@ns.expect(meal_edit)
	@ns.response(200, "Successfully edited the meal")
	@ns.response(400, "Invalid payload")
	def put(self, rest):
		with DBsession as session:
			try:
				if len(api.payload['new_fields']) == 0:
					raise KeyError

				fields = ('name', 'foodtype', 'price', 'description', 'image', 'available')
				query = session.query(
					Meal
				).filter(
					Meal.rest == rest,
					Meal.id == api.payload["meal_id"]
				).update({
					getattr(Meal, f_type) : api.payload['new_fields'][f_type]
					for f_type in fields if f_type in api.payload['new_fields']
				}, synchronize_session=False)
				session.commit()
				return {"message" : "Update successful"}, 200
			except (exc.ProgrammingError, KeyError):
				return {'message' : "Invalid payload"}, 400