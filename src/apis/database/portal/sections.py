from flask_restx import Resource
from sqlalchemy import exc
from sqlalchemy.sql import case

from . import DBsession, ns, api
from ..scheme import *

try:
	from ...utilities.models.portal import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.portal import *

for model in (sections_list, section_create, section_list, section_edit, section_items_edit):
	api.add_model(model.name, model)

@ns.route('/sections/<int:rest>')
class SectionManager(Resource):

	@ns.doc("Returns the restaurant's sections",
		params={
			'rest' : "Restaurant's id to get data from."
		}
	)
	@ns.response(200, "Successfully fetched sections", model=sections_list)
	def get(self, rest):
		with DBsession as session:
			query = session.query(MenuSection.name).filter(
				MenuSection.rest == rest
			).order_by(
				MenuSection.position
			)

		return { 'sections' : [item[0] for item in query.distinct().all()]}

	@ns.doc("Creates a restaurant section")
	@ns.expect(section_create)
	@ns.response(200, "Successfully created section")
	@ns.response(409, "Section already exists")
	def post(self, rest):
		with DBsession as session:
			try:
				section = MenuSection(name=api.payload['name'], rest=rest)
				session.add(section)
				session.commit()
				return {'message' : 'Section created successfully'}, 200
			except exc.IntegrityError:
				return {'message' : 'Section already exists'}, 409

	@ns.doc("Deletes the parsed restaurant's sections")
	@ns.expect(section_list)
	@ns.response(200, "Successfully deleted sections")
	@ns.response(404, "None of the parsed sections were found")
	def delete(self, rest):
		with DBsession as session:
			query = session.query(
				MenuSection
			).filter(
				MenuSection.rest == rest,
				MenuSection.name.in_(api.payload['names'])
			)
			if query.count() == 0:
				return {'message' : 'No sections found'}, 404

			query.delete(synchronize_session=False)
			session.commit()
			return {'message' : "Successfully deleted section(s)"}, 200


	@ns.doc("Edits a section")
	@ns.expect(section_edit)
	@ns.response(200, "Successfully edited the section")
	@ns.response(409, "Section already exists")
	def put(self, rest):
		with DBsession as session:
			try:
				query = session.query(
					MenuSection
				).filter(
					MenuSection.rest == rest,
					MenuSection.name == api.payload['old_name']
				).update({
					MenuSection.name : api.payload['new_name']
				}, synchronize_session=False)
				session.commit()
				return {"message" : "Update successful"}, 200
			except exc.IntegrityError:
				return {'message' : 'Section already exists'}, 409

@ns.route('/section/reorder/<int:rest>')
class SectionReorder(Resource):

	@ns.doc("Reorders the sections")
	@ns.expect(section_list)
	@ns.response(200, "Successfully edited the section")
	@ns.response(400, "Bad payload")
	def put(self, rest):
		size = len(api.payload['names'])
		bulk_update = {section : n+1+size for n, section in enumerate(api.payload['names'])}

		with DBsession as session:
			try:
				query = session.query(
					MenuSection
				).filter(
					MenuSection.rest == rest
				)

				# if the whole payload is in table, than filtering by the table contents
				# means it can't be smaller (cuz that would imply payload has an item the table doesn't).
				# And can't be bigger because the table has unicity on the names.
				# However, the table could have items the payload doesn't.
				payload_in_table = query.filter(MenuSection.name.in_(api.payload['names'])).count() == size

				# If table in payload, it means it can't be be bigger
				# because it would mean having an item the payload doesn't.
				# If it has the same size as payload and payload is in the table
				# (the statement above), then they are equal.
				table_in_payload = query.count() == size

				# if payload is not equal to table:
				if not (payload_in_table and table_in_payload):
					return {'message' : 'Invalid payload list'}, 400

				query.update({
					MenuSection.position : case(
						bulk_update,
						value=MenuSection.name
					)
				}, synchronize_session="fetch")

				query.update({
					MenuSection.position : MenuSection.position - size
				}, synchronize_session="fetch")

				session.commit()
				return {"message" : "Update successful"}, 200
			except KeyError:#exc.IntegrityError:
				return {'message' : 'Some conflict on ordering'}, 400

@ns.route('/section/meal/reorder/<int:rest>')
class SectionReorder(Resource):

	@ns.doc("Reorders the meals in the sections")
	@ns.response(200, "Successfully reordered the section")
	@ns.response(404, "Meal or section not found")
	def put(self, rest):
		with DBsession as session:
			session.query(
				MenuSectionRelation
			).filter(
				MenuSectionRelation.rest == rest,
				MenuSectionRelation.name == api.payload['section']
			).delete(synchronize_session="fetch")

			for n, meal_id in enumerate(api.payload['meals']):
				r = MenuSectionRelation(
					name=api.payload['section'],
					rest=rest,
					meal=meal_id,
					position=n+1
				)
				session.add(r)

			try:
				session.commit()
				return {'message' : "Successfully updated"}, 200
			except exc.ProgrammingError:
				return {'message' : 'Section or meal not found'}, 404