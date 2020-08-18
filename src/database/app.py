import os
import re
import json

from datetime import date, datetime

from flask import Flask, request
from flask_restx import Api, Resource, fields

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from .scheme import Base, User, Restaurant, Meal, FoodType, Cart, Item

app = Flask('Qfila-Database')
api = Api(app, version='0.1', title='Qfila-Database',
	description='A database REST interface for the Qfila application',
)

ns = api.namespace('database')

DATABASE_ENGINE = os.getenv('DATABASE_ENGINE')
engine = create_engine(DATABASE_ENGINE)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@ns.route('/user')
class UserHandler(Resource):

	def query(self, data):
		id_name = list(data)[0]

		if id_name in ("email", "phone"):
			return session.query(User).filter(User.__getattribute__(User, id_name) == data[id_name].lower())
		else:
			raise KeyError(f"{id_name} not email or phone")

	def age_check(self, d):
		"""Checks the age based on the (d)ate
			
			If it's below 12 years old:
				return False
			Else:
				return True
		"""

		if isinstance(d, str):
			d = date.fromisoformat(d)

		tdy = date.today()
		twelve_years_ago = date(tdy.year-12, tdy.month, tdy.day)

		return d <= twelve_years_ago


	def post(self):
		data = dict(request.form)

		try:
			#checking obligatory fields and modifying as required.
			data['birthday'] = date.fromisoformat(data['birthday'])
			if not self.age_check(data['birthday']):
				api.abort(403, "User below 12 years old")

			data['name'] = data['name'].lower()
			data['email'] = data['email'].lower()
			match = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", data['email'])
			if match is None:
				api.abort(400, "Invalid email.")

			data['passwd']

			user = User(**data)
			session.add(user)

			session.commit()
		except IntegrityError as e:
			api.abort(409, e._message().split(".")[-1] + " already in use.")
		except KeyError as e:
			"Required value is missing"
			api.abort(400, e.args[0])

		return {}, 201

	def get(self):
		data = dict(request.form)
		
		try:
			query = self.query(data)
			return query.first().serialize()
		except AttributeError:
			api.abort(404)
		except KeyError as e:
			api.abort(415, e.args[0])


	def put(self):
		data = json.loads(dict(request.form)['data'])

		if 'birthday' in data['update']:
			data['update']['birthday'] = date.fromisoformat(data['update']['birthday'])
			if not self.age_check(data['birthday']):
				api.abort(403, "User below 12 years old")

		try:
			query = self.query(data['id'])
			query.update(data['update'])
			session.commit()
			return {}, 200
		except AttributeError:
			api.abort(404)
		except KeyError as e:
			api.abort(415, e.args[0])

	def delete(self):
		data = dict(request.form)

		try:
			query = self.query(data)
			query.delete()
			session.commit()
			return {}, 200
		except AttributeError:
			api.abort(404)
		except KeyError as e:
			api.abort(415, e.args[0])


if __name__ == '__main__':
	app.run(debug=True)