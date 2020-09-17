from flask_restx import Resource
from flask_mail import Message

from .app import ns, api, mail

@ns.route('/passwordrecovery')
class PasswordRecovery(Resource):
	def post(self):
		link = api.payload['link']
		email = api.payload['email']

		msg = Message("Qfila esqueci minha senha", recipients=[email])
		msg.html = f'Você requisitou uma mudança de senha. <a href="{link}">Clique aqui</a>'

		mail.send(msg)

		return {'message' : 'email sent'}