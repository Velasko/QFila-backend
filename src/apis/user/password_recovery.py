import json

from markupsafe import escape
from requests import get, post, put

from flask import request, render_template_string, make_response

from flask_restx import Resource

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

from .app import ns, api, headers

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

try:
	from ..utilities import authentication, checkers
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, checkers

@ns.route('/passwordrecovery')
class PasswordRecovery(Resource):
	def post(self):

		#curl -X POST "http://localhost:5000/user/passwordrecovery" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{ \"email\" : \"f.l.velasko@gmail.com\"}"
		email = api.payload['email']

		user = get(
			'{}/database/user'.format(appmodule.app.config['DATABASE_URL']),
			data=json.dumps({'email': email}), headers=headers
		)

		if user.status_code == 404:
			api.abort(404, "Could not find user.")

		token = authentication.generate_token(
			{'email' : email},
			appmodule.app.config,
			duration=15
		)

		link = appmodule.app.config['APPLICATION_HOSTNAME'] + "/user/passwordrecovery/" + escape(token)

		email = post(
			'{}/mail/passwordrecovery'.format(appmodule.app.config['DATABASE_URL']),
			data=json.dumps({'link' : link, 'email' : email}), headers=headers
		)

		return email.json(), email.status_code, email.headers.items()

	@authentication.token_required(appmodule)
	def put(self, user):
		passwd = api.payload['passwd']

		data = {
			'id' : {
				'email' : user['email']
			},
			'update' : {
				'passwd' : passwd
			}
		}

		resp = put('{}/database/user'.format(appmodule.app.config['DATABASE_URL']),
			data=json.dumps(data), headers=headers
		)

		print(resp.status_code)

		return resp.json(), resp.status_code, resp.headers.items()


class NewPasswordForm(FlaskForm):
	passwd = PasswordField('Nova senha:', validators=[DataRequired()])
	verify = PasswordField('Verificação:', validators=[EqualTo('Nova senha')])
	submit = SubmitField('Atualizar')

@ns.route("/passwordrecovery/<string:token>")
class ForgottenPassword(Resource):
	def get(self, token, head=""):
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
		headers = {'Content-Type': 'text/html'}
		return make_response(render_template_string(template, form=NewPasswordForm()), 200, headers)

	def post(self, token):
		"""Verifier of the password.

		Will check if both fields are consistent and if they
		are valid."""
		passwd, verify = request.form['passwd'], request.form['verify']
		if passwd != verify:
			return self.get(token, head="Senhas diferentes")
		elif not checkers.valid_password(passwd):
			return self.get(token, head="Senha invalida")

		passwd = str(authentication.hash_password(passwd))
		print(passwd)

		header = headers.copy()
		header['token'] = token
		resp = put(
			'{}/user/passwordrecovery'.format(appmodule.app.config['DATABASE_URL']),
			data=json.dumps({'passwd': passwd}), headers=header
		)

		if resp.status_code == 200:
			return "Senha modificada com sucesso", resp.status_code, {'Content-Type': 'text/html'}