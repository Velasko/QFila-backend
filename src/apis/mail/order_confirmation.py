from flask_restx import Resource
from flask_mail import Message

from .app import ns, api, mail_scheduler

@ns.route('/orderreview')
class OrderReview(Resource):
	def post(self):
		data = api.payload

		email = data['email']
		recipients = data['recipients']
		msg = "{ORDER REVIEW HERE}"

		mail = {
			'subject' : 'order review',
			'recipients' : recipients,
			'html' : msg
		}

		mail_scheduler.append(msg)
		return {'message' : 'email added to queue'}, 201