import json

from requests import post

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

for model in (meal_info, rest, payment_model, order_contents, order):
	api.add_model(model.name, model)

@ns.route('/order')
class PlaceOrder(Resource):

	@ns.expect(order)
	@authentication.token_required()
	def post(self, user):
		"""This function expects a json with the fields "payment" and "order".
		 - Payment : Must parse the payment data. (Yet to know which are those)
		 - Order : A dictionary with the data of the order positioned as the following:

			{ rest_id : { meal_id : {meal_info} }, fee : value }
			
			mealinfo : { 
				"ammount" : ammount,
				"comment" : comment,
			}


		The meals data required are: meal and restaurant's id and the ammount.
		fee is an optional value. If not parsed, it'll be calculated as usual.
		"""
		data = api.payload
		order = data['order']
		payment_method = data['payment']['method']

		if 'fee' in order:
			fee = order['fee']

		resp = post('{}/database/user/order'.format(current_app.config['DATABASE_URL']),
			json={
				'user': user['email'],
				**api.payload
			},
			headers=headers.json
		)

		if resp.status_code == 201:
			payment.execute(data['payment'])

		resp = post('{}/mail/orderreview'.format(current_app.config['MAIL_URL']),
			json={
				'recipients' : {"name" : user['name'], "email" : user['email']},
				'order' : order
			},
			headers=headers.json
		)

		return {}, resp.status_code