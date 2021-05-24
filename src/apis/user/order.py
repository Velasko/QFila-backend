import json
import datetime

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

for model in (complement_model, meal_info, rest, payment_model, order_contents, order):
	api.add_model(model.name, model)

@ns.route('/order')
class PlaceOrder(Resource):

	@ns.response(201, "Method executed successfully.")
	@ns.response(400, "Bad payload")
	@ns.response(409, "This order was already processed")
	@ns.response(503, "Could not stablish connection to database")
	@authentication.token_required(namespace=ns, expect_args=[order])
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
					'time' : datetime.datetime.now().isoformat(),
					**api.payload
				},
				headers={**headers.json, **headers.system_authentication}
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		if resp.status_code == 201:
			payment.execute(data['payment'])
		elif resp.status_code in (400, 409):
			return resp.json(), resp.status_code
		else:
			# print(resp.status_code, resp.json())
			return {'message': "ERROR: user/order.py, line 51. Handle database errors"}, 500
			raise NotImplemented("user/order.py, line 51. Handle database errors")
			
		# resp = post('{}/mail/orderreview'.format(current_app.config['MAIL_URL']),
		# 	json={
		# 		'recipients' : {"name" : user['name'], "email" : user['email']},
		# 		'order' : order
		# 	},
		# 	headers=headers.json
		# )

		return {'message' : 'order completed'}, resp.status_code