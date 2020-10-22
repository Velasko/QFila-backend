import json

from requests import post, exceptions

from flask import current_app
from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, headers, payment
	from ..utilities.models.order import *
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, headers, payment
	from utilities.models.order import *

for model in (meal_info, rest, payment_model, order_contents, order, recipient_model, mail_order):
	api.add_model(model.name, model)

@ns.route('/order')
class PlaceOrder(Resource):

	@ns.response(503, "Could not stablish connection to database")
	@authentication.token_required(namespace=ns, expect_args=[mail_order])
	def post(self, user):
		"""Method to make the order

		Data will be sent to the database, send an email"""
		data = api.payload
		order = data['order']
		payment_method = data['payment']['method']

		if 'fee' in order:
			fee = order['fee']

		try:
			resp = post('{}/database/user/order'.format(current_app.config['DATABASE_URL']),
				json={
					'user': user['email'],
					**api.payload
				},
				headers=headers.json
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		if resp.status_code == 201:
			payment.execute(data['payment'])
		else:
			raise NotImplemented("user/order.py, line 51. Handle database errors")
			

		resp = post('{}/mail/orderreview'.format(current_app.config['MAIL_URL']),
			json={
				'recipients' : {"name" : user['name'], "email" : user['email']},
				'order' : order
			},
			headers=headers.json
		)

		return {'message' : 'order completed'}, resp.status_code