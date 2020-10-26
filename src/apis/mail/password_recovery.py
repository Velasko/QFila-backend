from flask_restx import Resource
from flask_mail import Message

from .app import ns, api, mail_scheduler

try:
	from ..utilities.models.mail import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.mail import *

for model in (recipient_model, recipient_model, email_model, recover_passwd_model):
	api.add_model(model.name, model)

@ns.route('/passwordrecovery')
class PasswordRecovery(Resource):

	@ns.expect(recover_passwd_model)
	@ns.response(201, "Email added to the queue")
	def post(self):
		link = api.payload['link']
		recipients = [list(recipient.values()) for recipient in api.payload['recipients']]

		msg = {
			'subject' : "Requisição de mudança de senha do Qfila",
			'recipients' : recipients,
			'html' : f'Você requisitou uma mudança de senha. <a href="{link}">Clique aqui</a>'
		}

		mail_scheduler.append(msg)
		return {'message' : 'email added to queue'}, 201

@ns.route("/passwordrecovery/notify")
class NotifyPasswordRecovery(Resource):

	@ns.expect(email_model)
	@ns.response(201, "Email added to the queue")
	def post(self):
		recipients = [list(recipient.values()) for recipient in api.payload['recipients']]

		msg = {
			'subject' : "Senha modificada com sucesso!",
			'recipients' : recipients,
			'html' : f'Olá, {recipients[0][0]}! Sua senha Qfila foi modificada com sucesso.'
		}

		mail_scheduler.append(msg)
		return {'message' : 'email added to queue'}, 201