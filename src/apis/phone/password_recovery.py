from flask_restx import Resource

from .app import ns, api, sms_service

try:
	from ..utilities.models.phone import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.phone import *

for model in (recipient_model, phone_model, recover_passwd_model):
	api.add_model(model.name, model)

@ns.route('/passwordrecovery')
class PasswordRecovery(Resource):

	@ns.expect(recover_passwd_model)
	@ns.response(201, "SMS successfully sent")
	@ns.response(206, "SMS sent, but couldn't storage it's ID in the database")
	@ns.response(413, "SMS message was too large")
	@ns.response(424, "Error with AWS")
	def post(self):
		link = api.payload['link']
		client_id = api.payload['client']
		msg = f"Link para mudança de senha do Qfila: {link}"

		phone = api.payload['phone']

		return sms_service.send_message(message=msg, phone=phone, client=client_id, operation="/passwordrecovery")


@ns.route("/passwordrecovery/notify")
class NotifyPasswordRecovery(Resource):

	@ns.expect(phone_model)
	@ns.response(201, "SMS successfully sent")
	@ns.response(206, "SMS sent, but couldn't storage it's ID in the database")
	@ns.response(413, "SMS message was too large")
	@ns.response(424, "Error with AWS")
	def post(self):
		phone = api.payload['phone']
		client_id = api.payload['client']
		msg = "Sua senha Qfila foi alterada com sucesso!"

		return sms_service.send_message(message=msg, phone=phone, client=client_id, operation='/passwordrecovery/notify')