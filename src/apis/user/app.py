import datetime
import json
import jwt
import os

from requests import post, get, put, delete

from flask import Flask, request
from flask_restx import Api, Resource, fields, reqparse

#login
from flask_login import LoginManager, login_user

#password hash
from werkzeug.security import generate_password_hash, check_password_hash


hostname = os.getenv('APPLICATION_HOSTNAME')

headers = {
	"accept": "application/json",
	"Content-Type": "application/json"
}

api = Api(version='0.1', title='Client',
    description='Client side interface',
)

ns = api.namespace('user', description='client operations')

user = api.model('User', {
    'email': fields.String(readonly=True, description='User email'),
    'passwd': fields.String(attribute='password', required=True, description='User password'),
})

@ns.route("/login")
class Auth(Resource):

	@ns.doc("User authentication")
	@ns.expect(user)
	def get(self):
		"""Method to be authenticated"""
		auth = api.payload

		resp = get(f'{hostname}/database/user', data=json.dumps({'email': auth['email']}), headers=headers)
		user = resp.json()

		if check_password_hash(user['passwd'], auth['passwd']):
			token = jwt.encode({
				'public_id' : user['email'],
				'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
				ns.app.config['SECRET_KEY']
			)

			return {'token' : token.decode('UTF-8')}, 200
		else:
			return {}, 401

	# should this even be here?
	def update(self):
		"""Method to modify password?"""
		pass

	def post(self):
		"""method to create the login"""
		data = api.payload

		for key, value in data.items():
			if key == 'passwd':
				data['passwd'] = generate_password_hash(data['passwd'], 'sha256')
			else:
				data[key] = value.lower()

		resp = post(f'{hostname}/database/user', data=json.dumps(data), headers=headers)

	def delete(self):
		"""method to logout"""
		pass


class Hist():
	# raise NotImplementedError("User purchase history not implemented")

	def post():
		"""A purchase has been made"""
		pass

	def get():
		"""Get purchase history"""
		pass

if __name__ == '__main__':
	app = Flask("Qfila user")
	api.init_app(app)
	app.run()