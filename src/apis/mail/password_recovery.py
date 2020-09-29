from flask_restx import Resource
from flask_mail import Message

from .app import ns, api, mail_scheduler

@ns.route('/passwordrecovery')
class PasswordRecovery(Resource):
	def post(self):
		link = api.payload['link']
		email = api.payload['email']
		name = api.payload['name']

		msg = {
			'subject' : "Requisição de mudança de senha do Qfila",
			'recipients' : [(name, email)],
			'html' : f'Você requisitou uma mudança de senha. <a href="{link}">Clique aqui</a>'
		}

		mail_scheduler.append(msg)
		return {'message' : 'email added to queue'}, 201