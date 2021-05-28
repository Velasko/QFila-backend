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
	from ...utilities.models.user import *
except ValueError:
	#If running from inside apis folder
	from utilities import checkers
	from utilities.models.user import *

api.add_model(id.name, id)
api.add_model(user.name, user)

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

@ns.route('/')
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

		with DBsession as session:
			data = api.payload
			try:
				#checking obligatory fields and modifying as required.
				try:
					data['birthday'] = date.fromisoformat(data['birthday'])
					if not checkers.age_check(data['birthday']):
						return {'message' : "User below 12 years old"}, 403
				except ValueError:
					return {'message': "Invalid data format."}, 400

				data['name'] = data['name'].lower()
				data['email'] = data['email'].lower()

				if not checkers.valid_email(data['email']):
					return {'message': "Invalid email."}, 400

				data['passwd']

				user = User(**data)
				session.add(user)

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
class UserHandler_UrlParse(Resource):

	@ns.doc("Find and return user based on phone or email")
	@ns.response(200, "Method executed successfully.", model=user)
	@ns.response(404, "User not found.")
	def get(self, login):
		"""Method to get user information based on e-mail or phone.
		A single user shall be returned from this query."""

		path = request.full_path.split("/")
		return common.user.fetch_user(User, path[-2], login)

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

		with DBsession as session:
			try:
				data, field = get_data(email, phone)
				update = api.payload

				if 'birthday' in update:
					try:
						update['birthday'] = date.fromisoformat(update['birthday'])
						if not checkers.age_check(update['birthday']):
							return {'message' : "User below 12 years old"}, 403
					except ValueError:
						return {'message': "Invalid data format."}, 400

				if 'email' in update:
					if not checkers.valid_email(update['email']):
						return {'message' : "Invalid email."}, 400

				query = session.query(User).filter(field == data)
				if query.count() == 0:
					return {'message' : 'No user with such id'}, 404
				query.update(update)
				session.commit()
				return {'message' : 'update sucessfull'}, 200
			except KeyError as e:
				return {'message' : e.args[0]}, 400
			except exc.IntegrityError as e:
				return {'message' : e._message().split(".")[-1][:-3] + " already in use."}, 409
			except Exception:
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

		with DBsession as session:
			try:
				data, field = get_data(email, phone)

				query = session.query(User).filter(field == data)
				if query.count() == 0:
					return {'message' : 'No user with such id'}, 404
				query.delete()
				session.commit()
				return {}, 200
			except Exception as e:
				return {'message' : e.args[0]}, 500