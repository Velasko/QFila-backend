from flask_restx import Resource
from flask_mail import Message

from .app import ns, api, mail_scheduler

try:
	from ..utilities.models.mail import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.mail import *

for model in (recipient_model, email_model, recover_passwd_model):
	api.add_model(model.name, model)

@ns.route('/passwordrecovery')
class PasswordRecovery(Resource):

	@ns.expect(recover_passwd_model)
	@ns.response(201, "Email added to the queue")
	def post(self):
		link = api.payload['link']
		recipients = [recipient.values() for recipient in api.payload['recipients']]

		msg = {
			'subject' : "Requisição de mudança de senha do Qfila",
			'recipients' : [(name, email)],
			'html' : f'Você requisitou uma mudança de senha. <a href="{link}">Clique aqui</a>'
		}

		mail_scheduler.append(msg)
		return {'message' : 'email added to queue'}, 201