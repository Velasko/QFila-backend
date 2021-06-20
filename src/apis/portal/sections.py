import requests

from flask import current_app
from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, headers
	from ..utilities.models.portal import *
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, headers
	from utilities.models.portal import *

for model in (sections_list, section_create, section_list, section_edit, section_items_edit):
	api.add_model(model.name, model)

@ns.route('/section/manager')
class SectionManager(Resource):

	@ns.doc("Menu section fetching")
	@authentication.token_required(namespace=ns)
	@ns.response(200, "Sections successfully fetched", model=sections_list)
	def get(self, rest):
		resp = requests.get(
			'{}/database/portal/sections/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

	@ns.doc("Create new section")
	@authentication.token_required(namespace=ns, expect_args=[section_create])
	@ns.response(200, "Successfully created section")
	@ns.response(409, "Section already exists")
	def post(self, rest):
		resp = requests.post(
			'{}/database/portal/sections/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

	@ns.doc("Delete a section")
	@authentication.token_required(namespace=ns, expect_args=[section_list])
	@ns.response(200, "Successfully deleted sections")
	@ns.response(404, "None of the parsed sections were found")
	def delete(self, rest):
		resp = requests.delete(
			'{}/database/portal/sections/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

	@ns.doc("Edits a section")
	@authentication.token_required(namespace=ns, expect_args=[section_edit])
	@ns.response(200, "Successfully edited the section")
	@ns.response(409, "Section already exists")
	def put(self, rest):
		resp = requests.put(
			'{}/database/portal/sections/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

@ns.route('/section/reorder')
class SectionReorder(Resource):

	@ns.doc("Reorders the sections")
	@authentication.token_required(namespace=ns, expect_args=[section_list])
	@ns.response(200, "Successfully reordered the sections")
	@ns.response(400, "Bad payload. Maybe not every section parsed")
	def put(self, rest):
		resp = requests.put(
			'{}/database/portal/section/reorder/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code

@ns.route("/section/meal/reorder")
class SectionMealReorder(Resource):

	@ns.doc("Reorders the meals in the sections")
	@authentication.token_required(namespace=ns, expect_args=[section_items_edit])
	@ns.response(200, "Successfully reordered the section")
	@ns.response(404, "Meal or section not found")
	def put(self, rest):
		resp = requests.put(
			'{}/database/portal/section/meal/reorder/{}'.format(
				current_app.config['DATABASE_URL'],
				rest['id']
			),
			json=api.payload,
			headers={**headers.json, **headers.system_authentication}
		)

		return resp.json(), resp.status_code