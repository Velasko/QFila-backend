import json

from requests import post

from flask_restx import Resource

from .app import ns, api

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

try:
	from ..utilities import authentication, headers, payment
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, headers, payment

@ns.route('/order')
class PlaceOrder(Resource):

	@authentication.token_required(appmodule)
	def post(self, user):
		"""This function expects a json with the fields "payment" and "order".
		 - Payment : Must parse the payment data. (Yet to know which are those)
		 - Order : A dictionary with the data of the order positioned as the following:

			{ rest_id : { meal_id : ammount } }

		The meals data required are: meal and restaurant's id and the ammount.
		"""
		data = api.payload
		order = data['order']

		resp = post('{}/database/user/order/'.format(appmodule.app.config['DATABASE_URL']),
			json={
				'user': user['email'],
				'order' : order
			},
			headers=headers.json
		)

		if resp.status_code == 201:
			payment.execute(data['payment'])

		resp = post('{}/mail/orderreview'.format(appmodule.app.config['APPLICATION_HOSTNAME']),
			json={
				'recipients' : (user['name'], user['email']),
				'order' : order
			},
			headers=headers.json
		)

		return {}, resp.status_code