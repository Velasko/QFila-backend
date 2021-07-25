import requests

from flask import current_app
from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, headers
	from ..utilities.models.portal import *
	from ..utilities.models.database import meal
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, headers
	from utilities.models.portal import *
	from utilities.models.database import meal


for model in (meal, meal_create, meal_edit, meal_list, compl_repr):
	api.add_model(model.name, model)

@ns.route('/meal/fetch')
class MealFetcher(Resource):
	@ns.doc("Menu meal fetching")
	@authentication.token_required(namespace=ns, expect_args=[meal_list])
	@ns.response(200, "Sections successfully fetched", model=meal)
	def post(self, rest):
		"""
Method to fetch the meal's data.
If only certain meals are desired, it may be parsed in the payload.
It will return every meal otherwise.
		"""
		resp = requests.post(
			'{}/database/portal/meals/fetch/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

@ns.route('/meal/manager')
class MealManager(Resource):

	@ns.doc("Create new meal")
	@authentication.token_required(namespace=ns, expect_args=[meal_create])
	@ns.response(200, "Successfully created meal")
	@ns.response(409, "Section already exists")
	def post(self, rest):
		"""Method to create meal."""
		resp = requests.post(
			'{}/database/portal/meals/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

	@ns.doc("Edits a meal")
	@authentication.token_required(namespace=ns, expect_args=[meal_edit])
	@ns.response(200, "Successfully edited the section")
	@ns.response(409, "Section already exists")
	def put(self, rest):
		"""Method to modify meal."""
		resp = requests.put(
			'{}/database/portal/meals/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code