import requests

from flask import request, current_app
from flask_restx import Resource

from .app import ns, api
from .common import pagination, force

try:
	from ..utilities import authentication, headers
	from ..utilities.models.portal import *
	from ..utilities.models.database import compl_item, meal
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, headers
	from utilities.models.portal import *
	from utilities.models.database import compl_item, meal

for model in (meal, compl_item, complement_list, complement_item, complement_create, complement_edit):
	api.add_model(model.name, model)

@ns.route('/complement/fetch')
class ComplementFetcher(Resource):

	@ns.doc("Menu complement fetching")
	@authentication.token_required(namespace=ns, expect_args=[pagination, complement_list])
	@ns.response(200, "Sections successfully fetched", model=meal)
	def post(self, rest):
		"""
Method to fetch the complement's data.
If only certain complement are desired, it may be parsed in the payload.
It will return every complement otherwise.
		"""
		page_data = dict(request.args)
		payload = api.payload.copy()
		payload['limit'] = min(max(1, int(page_data['pagesize'])), current_app.config['PORTAL_MAX_PAGE_SIZE'])
		payload['offset'] = (max(0, int(page_data['page']) - 1)) * payload['limit']

		resp = requests.post(
			'{}/database/portal/complements/fetch/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

@ns.route('/complement/manager')
class ComplementManager(Resource):

	@ns.doc("Create new complement")
	@authentication.token_required(namespace=ns, expect_args=[complement_create])
	@ns.response(200, "Successfully created complement")
	@ns.response(409, "Section already exists")
	def post(self, rest):
		"""Method to create complement."""
		resp = requests.post(
			'{}/database/portal/complements/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

	@ns.doc("Edits a complement")
	@authentication.token_required(namespace=ns, expect_args=[complement_edit])
	@ns.response(200, "Successfully edited the section")
	@ns.response(409, "Section already exists")
	def put(self, rest):
		"""Method to modify complement."""
		resp = requests.put(
			'{}/database/portal/complements/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

	@ns.doc("Menu complement deleting")
	@authentication.token_required(namespace=ns, expect_args=[force, complement_list])
	@ns.response(200, "Complements successfully deleted")
	@ns.response(403, "Complement has meal relations", model=meal_list)
	def delete(self, rest):
		"""Method to delete complement."""
		print(dict(request.args))
		return

		resp = requests.put(
			'{}/database/portal/complements/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json={**api.payload},
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code