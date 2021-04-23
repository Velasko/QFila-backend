import json

import jwt
import jwt.exceptions

from markupsafe import escape
from requests import get, post, put, exceptions

from flask import request, render_template_string, make_response, current_app

from flask_restx import Resource

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

from .app import ns, api

try:
	from ..utilities import authentication, checkers, headers
	from ..utilities.models.user import id, passwd
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, checkers, headers
	from utilities.models.user import id, passwd

for model in (id, passwd):
	api.add_model(model.name, model)

@ns.route('/passwordrecovery')
class PasswordRecovery(Resource):

	@ns.expect(id)
	@ns.response(201, "Message to be sent")
	@ns.response(404, "User not found")
	@ns.response(503, "Email, phone or database unavailable.")
	def post(self):

		if 'email' in api.payload:
			key = 'email'
		else:
			key = 'phone'

		value = api.payload[key]

		try:
			user = get(
				'{}/database/user/{}/{}'.format(current_app.config['DATABASE_URL'], key, value),
				headers=headers.system_authentication
			)
		except exceptions.ConnectionError:
			return {'message' : "database service unavailable"}, 503

		if user.status_code == 404:
			api.abort(404, "Could not find user.")

		user = user.json()

		token = authentication.generate_token(
			{key : value, 'passwd' : user['passwd']},
			current_app.config,
			duration=50 #minutes
		)

		link = current_app.config['APPLICATION_HOSTNAME'] + "/user/passwordrecovery/" + escape(token)

		if key == 'email':
			try:
				email = post(
					'{}/mail/passwordrecovery'.format(current_app.config['MAIL_URL']),
					data=json.dumps({'link' : link, 'recipients' : [{'email' : value, 'name': user['name']}]}),
					headers={**headers.json, **headers.system_authentication}
				)
				if email.status_code == 404:
					raise exceptions.ConnectionError

			except exceptions.ConnectionError:
				return {'message' : "email service unavailable"}, 503

			return email.json(), email.status_code, email.headers.items()

		elif key == 'phone':
			try:
				phone = post(
					'{}/phone/passwordrecovery'.format(current_app.config['PHONE_URL']),
					data=json.dumps({'link' : link, 'user': user['id'], 'phone' : value}),
					headers={**headers.json, **headers.system_authentication}
				)

				return phone.json(), phone.status_code, phone.headers.items()
			except exceptions.ConnectionError:
				return {'message' : 'phone service unavailable'}, 504

		else:
			return {'message' : 'Unexpected behaviour'}, 500

@ns.route('/changepassword')
class ChangePassword(Resource):

	@ns.response(200, "Password modified successfully.")
	@ns.response(503, "Database/email/phone service unavailable.")
	@authentication.token_required(namespace=ns, expect_args=[passwd])
	def put(self, user):
		"""Official method to modify the user's password"""
		#Generating password hash
		passwd = api.payload['passwd']
		passwd_hash = authentication.hash_password(passwd)

		#Verifying the hash is properly working
		try:
			authentication.passwd_check(passwd_hash, passwd)
		except KeyError:
			return {'message' : 'error in hashing password'}, 500

		#Generating payload to send to database
		data = {
			'passwd' : passwd_hash
		}

		if not user['email'] is None:
			key = 'email'
		else:
			key = 'phone'

		#Updating password in database
		try:
			resp = put('{}/database/user/{}/{}'.format(
					current_app.config['DATABASE_URL'],
					key,
					user[key]
				),
				data=json.dumps(data), headers={**headers.json, **headers.system_authentication}
			)
		except exceptions.ConnectionError:
			return {'message' : "database service unavailable"}, 503

		if resp.status_code != 200:
			return {'message' : 'Unexpected answer from database'}, 500
		
		#Notifying user of password change
		if key == 'email':
			try:
				resp = post('{}/mail/passwordrecovery/notify'.format(current_app.config['MAIL_URL']),
					data=json.dumps({'recipients' : [{
						"name": user['name'],
						"email": user['email']
					}]}),
					headers={**headers.json, **headers.system_authentication}
				)
			except exceptions.ConnectionError:
				return {'message' : "email service unavailable"}, 503
		else:#if key == 'phone':
			raise NotImplemented('Phone service unimplemented')

		if resp.status_code != 201:
			print(resp.json())
			return {'message' : 'Unexpected answer from mail service', 'mail' : resp.json()}, 500

		return resp.json(), 200, resp.headers.items()


class NewPasswordForm(FlaskForm):
	passwd = PasswordField('Nova senha:', validators=[DataRequired()])
	verify = PasswordField('Verificação:', validators=[EqualTo('Nova senha')])
	submit = SubmitField('Atualizar')

@ns.route("/passwordrecovery/<string:token>")
class ForgottenPassword(Resource):

	@ns.response(200, "Web page loaded")
	@ns.response(498, "Token expired or invalid")
	@ns.response(503, "Could not stablish connection to database")
	def get(self, token, head=""):
		"""Simple page to insert new password

		It verifies if the token parsed in the url is valid.
		The form submits a post to the same url.

		FUTURE: this page shall be modified for a proper one

		ANALYZE: is it better to return invalid or expired? Or just a 404?
			for debugging it's easier token info
		"""
		try:
			data = jwt.decode(token, current_app.config['SECRET_KEY'])
		except jwt.exceptions.ExpiredSignatureError:
			return {'message' : 'Token expired'}, 498
		except jwt.exceptions.InvalidSignatureError:
			return {'message' : 'Token invalid'}, 498
		#Change to 404?

		if 'email' in data:
			key = 'email'
		else:
			key = 'phone'

		value = data[key]

		try:
			user = get(
				'{}/database/user/{}/{}'.format(current_app.config['DATABASE_URL'], key, value),
				headers={**headers.json, **headers.system_authentication}
			).json()
		except exceptions.ConnectionError:
			return {'message': 'Could not stablish connection to database'}, 503

		try:
			if data['passwd'] != user['passwd']:
				api.abort(404)
		except Exception:
			api.abort(404)

		template = head + """
{% block content %}
	<h1>Sign In</h1>
	<form action="" method="post" novalidate>
		{{ form.hidden_tag() }}
		<p>
			{{ form.passwd.label }}<br>
			{{ form.passwd() }}
		</p>
		<p>
			Verifica&#231;&#227;o:<br>
			{{ form.verify() }}
		</p>
		<p>{{ form.submit() }}</p>
	</form>
{% endblock %}
"""
		
		header = {'Content-Type': 'text/html'}
		return make_response(render_template_string(template, form=NewPasswordForm()), 200, header)

	@ns.response(200, "Password modified successfully")
	@ns.response(503, "Could not stablish connection to database")
	def post(self, token):
		"""Verifier of the password.

		Will check if both fields are consistent and if they
		are valid.

		If they are, modifies the password in the database service.
		"""
		passwd, verify = request.form['passwd'], request.form['verify']
		if passwd != verify:
			return self.get(token, head="Senhas diferentes")
		elif not checkers.valid_password(passwd):
			return self.get(token, head="Senha invalida")

		header = headers.json.copy()
		header['token'] = token

		try:
			resp = put(
				'{}/user/changepassword'.format(current_app.config['APPLICATION_HOSTNAME']),
				data=json.dumps({'passwd': passwd}), headers=header
			)
		except exceptions.ConnectionError:
			return {'message' : "service unavailable"}, 503

		if resp.status_code == 200:
			return "Senha modificada com sucesso", resp.status_code, {'Content-Type': 'text/html'}

		return resp.json(), resp.status_code

		#send notification of password change (email/phone)