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
		 - Order : A dictionary with the values as the meal's data. The keys are irrelevant.

		The meals data required are: meal and restaurant's id and the ammount.
		"""
		data = api.payload


		resp = post('{}/database/user/order/'.format(appmodule.app.config['DATABASE_URL']),
			json={
				'user': user['email'],
				'order' : data['order']
			},
			headers=headers.json
		)

		if resp.status_code == 201:
			payment.execute(data['payment'])

		return {}, resp.status_code