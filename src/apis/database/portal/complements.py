from flask_restx import Resource
from sqlalchemy import exc
from sqlalchemy.sql import case

from . import DBsession, ns, api
from ..scheme import *

try:
	from ...utilities.models.portal import *
	from ...utilities.models.database import meal
except ValueError:
	#If running from inside apis folder
	from utilities.models.portal import *
	from utilities.models.database import meal

for model in (meal, complement_item, db_complement_list, complement_item, complement_create, complements_data, complement_edit, complement_delete):
	api.add_model(model.name, model)

@ns.route('/complements/fetch/<int:rest>')
class ComplementFetcher(Resource):

	@ns.doc("Returns the restaurant's complements")
	@ns.expect(db_complement_list)
	@ns.response(200, "Successfully fetched sections", model=complements_data)
	def post(self, rest):
		with DBsession as session:
			query = session.query(
				Complement
			).filter(
				Complement.rest == rest
			)

			if 'complements' in api.payload:
				query = query.filter(
					Meal.id.in_(api.payload['complements'])
				)

			query = query.offset(api.payload['offset']).limit(api.payload['limit'])

			response = [compl.serialize() for compl in query.all()]
			for compl in response:
				items = session.query(
					ComplementItem.name, ComplementItem.price
				).filter(
					ComplementItem.rest == rest,
					ComplementItem.compl == compl['id']
				).order_by(
					ComplementItem.position
				).all()
				compl['items'] = [[item[0], float(item[1])] for item in items]

		return {'complements' : response}, 200

@ns.route("/complements/<int:rest>")
class ComplementManager(Resource):

	@ns.doc("Creates a restaurant complement")
	@ns.expect(complement_create)
	@ns.response(200, "Successfully created complement")
	@ns.response(400, "Invalid payload")
	@ns.response(409, "complement already exists")
	def post(self, rest):
		return

	@ns.doc("Edits a complement")
	@ns.expect(complement_edit)
	@ns.response(200, "Successfully edited the complement")
	@ns.response(400, "Invalid payload")
	def put(self, rest):
		return

	@ns.doc("Deletes a complement")
	@ns.expect(complement_delete)
	@ns.response(200, "Successfully edited the complement")
	@ns.response(400, "Invalid payload")
	def delete(self, rest):
		pass