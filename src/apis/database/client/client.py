import json
import re

from datetime import date

from flask import request
from flask_restx import Resource

from sqlalchemy import exc

from . import DBsession, ns, api
from .. import common
from ..scheme import *

try:
	from ...utilities import checkers
	from ...utilities.models.client import *
except ValueError:
	#If running from inside apis folder
	from utilities import checkers
	from utilities.models.client import *

api.add_model(id.name, id)
api.add_model(client.name, client)

def get_data(email, phone) -> (str, str):
	"""Gets email and phone.
	Returns a tuple with the first item being the data and the second
	the field name.
	"""
	if not email is None:
		field = Client.email 
		data = email
	elif not phone is None:
		data = phone
		field = Client.phone
	else:
		raise KeyError("No argument parsed")
	return data, field

@ns.route('/register')
class ClientHandler(Resource):

	@ns.doc("Create client")
	@ns.expect(client)
	@ns.response(201, "Method executed successfully.")
	@ns.response(400, "Invalid payload; missing the required argument in 'missing' field of return")
	@ns.response(403, "Birthday is less than 12 years ago.")
	@ns.response(409, "Email or phone already used.")
	def post(self):
		"""Method to create the client.
		"""

		with DBsession as session:
			data = api.payload
			try:
				#checking obligatory fields and modifying as required.
				try:
					data['birthday'] = date.fromisoformat(data['birthday'])
					if not checkers.age_check(data['birthday']):
						return {'message' : "Client below 12 years old"}, 403
				except ValueError:
					return {'message': "Invalid data format."}, 400

				data['name'] = data['name'].lower()
				data['email'] = data['email'].lower()

				if not checkers.valid_email(data['email']):
					return {'message': "Invalid email."}, 400

				data['passwd']

				client = Client(**data)
				session.add(client)

				session.commit()
			except exc.IntegrityError as e:
				message = e._message()
				key, value = re.findall('Key \((.+)\)=\((.+)\) already exists.', message)[0]
				api.abort(409, key + " already exists.")
			except KeyError as e:
				"Required value is missing"
				return {'missing' : e.args[0]}, 400

			return {}, 201

@ns.route('/phone/<string:login>')
@ns.route('/email/<string:login>')
class ClientHandler_UrlParse(Resource):

	@ns.doc("Find and return client based on phone or email")
	@ns.response(200, "Method executed successfully.", model=client)
	@ns.response(404, "Client not found.")
	def get(self, login):
		"""Method to get client information based on e-mail or phone.
		A single client shall be returned from this query."""

		path = request.full_path.split("/")
		return common.user.fetch_user(Client, path[-2], login)

	@ns.doc("Modify client")
	@ns.expect(client)
	@ns.response(200, "Method executed successfully.")
	@ns.response(400, "Query invalid.")
	@ns.response(403, "Birthday is less than 12 years ago.")
	@ns.response(404, "Client not found.")
	@ns.response(409, "Email or phone already used.")
	def put(self, login):
		"""Method to modify an client.

		The client identification must be parsed by the url, using either phone or email.
		The fields to be updated must be parsed on the payload.
		"""
		update_data = api.payload

		if 'birthday' in update_data:
			try:
				update_data['birthday'] = date.fromisoformat(update_data['birthday'])
				if not checkers.age_check(update_data['birthday']):
					return {'message' : "Client below 12 years old"}, 403

			except ValueError:
				return {'message': "Invalid data format."}, 400

		path = request.full_path.split("/")
		return common.user.update_user(Client, path[-2], login, update_data)

	@ns.doc("Delete client")
	@ns.response(200, "Method executed successfully.")
	@ns.response(404, "Client not found.")
	def delete(self, email=None, phone=None):
		"""Method called to delete the client.

		In this scenario, it was prefered to clear out the fields and turn it into
		a ghost client instead. (maybe -> Must verify with protection of data law)

		So far, the client is indeed deleted, if there is no history attached to it.
		"""

		with DBsession as session:
			try:
				data, field = get_data(email, phone)

				query = session.query(Client).filter(field == data)
				if query.count() == 0:
					return {'message' : 'No client with such id'}, 404
				query.delete()
				session.commit()
				return {}, 200
			except Exception as e:
				return {'message' : e.args[0]}, 500