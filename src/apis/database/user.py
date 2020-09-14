import json

from datetime import date
from flask_restx import Resource, fields
from sqlalchemy import exc

from .app import ns, session, api
from .scheme import Base, User, FoodCourt, Restaurant, Meal, FoodType, Cart, Item, safe_serialize

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

try:
	from ..utilities import checkers
except ValueError:
	#If running from inside apis folder
	from utilities import checkers

id = api.model('Identifyiers', {
	'email' : fields.String(required=True, description='User email'),
	'phone' : fields.Integer(description='User phone number')
})

user = api.inherit('User', id, {
	'name' : fields.String(required=True,description='User name'),
	'email' : fields.String(required=True, description='User email'),
	'passwd' : fields.String(required=True, description='User password'),
	'birthday' : fields.DateTime(required=True, description='User birthday', dt_format="iso8601"),
	'phone' : fields.Integer(default=None, description='User phone number')
})

@ns.route('/user')
class UserHandler(Resource):

	def query(self, data):
		id_name = list(data)[0]

		if id_name in ("email", "phone"):
			return session.query(User).filter(User.__getattribute__(User, id_name) == data[id_name].lower())
		else:
			raise KeyError(f"{id_name} not email or phone")

	@ns.doc("Create user")
	@ns.expect(user)
	def post(self):
		"""Method to create the user.

		Expected a json with the folowing items:

		Obligatory:
			- name
			- email
			- password (already hashed)
			- birthday (YYYY-MM-DD)

		Optional:
			- phone
		"""
		data = api.payload

		try:
			#checking obligatory fields and modifying as required.
			data['birthday'] = date.fromisoformat(data['birthday'])
			if not checkers.age_check(data['birthday']):
				api.abort(403, "User below 12 years old")

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
			api.abort(400, e.args[0])

		return {}, 201

	@ns.doc("Find user")
	@ns.expect(id)
	@ns.marshal_with(user)
	def get(self):
		"""Method to get user information based on e-mail or phone.
		A single user shall be returned from this query."""
		data = api.payload

		try:
			query = self.query(data)
			user = query.first().serialize()

			#hiding user id
			del user['id']

			return user
		except AttributeError:
			api.abort(404, 'User not found')
		except KeyError as e:
			api.abort(415, e.args[0])

	@ns.doc("Modify user")
	def put(self):
		"""Method to modify an user.

		A json with two sections must be parsed. 

		The first one must be named 'id' and must have unique identifyiers (email or phone).

		The second must be named update and have the fields to be updated.
		"""
		data = json.loads(dict(request.form)['data'])

		if 'birthday' in data['update']:
			data['update']['birthday'] = date.fromisoformat(data['update']['birthday'])
			if not checkers.age_check(data['birthday']):
				api.abort(403, "User below 12 years old")

		try:
			query = self.query(data['id'])
			query.update(data['update'])
			session.commit()
			return {}, 200
		except AttributeError:
			session.rollback()
			api.abort(404)
		except KeyError as e:
			session.rollback()
			api.abort(415, e.args[0])

	@ns.doc("Delete user")
	@ns.expect(id)
	def delete(self):
		"""Method called to delete the user.

		In this scenario, it was prefered to clear out the fields and turn it into
		a ghost user instead."""
		data = api.payload

		try:
			query = self.query(data)
			query.delete()
			session.commit()
			return {}, 200
		except AttributeError:
			session.rollback()
			api.abort(404)
		except KeyError as e:
			session.rollback()
			api.abort(415, e.args[0])