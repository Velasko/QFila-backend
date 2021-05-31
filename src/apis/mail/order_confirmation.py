import json

from requests import get, exceptions

from flask import current_app
from flask_restx import Resource
from flask_mail import Message

from .app import ns, api, mail_scheduler
from . import template

try:
	from ..utilities import headers, payment
	from ..utilities.models import client, mail
except ValueError:
	#If running from inside apis folder
	from utilities import headers, payment
	from ..utilities.models import client, mail

for model in (client.history_complements, client.history_items, client.history_order, mail.history):
	api.add_model(model.name, model)

@ns.route('/orderreview')
class OrderReview(Resource):
	def decode(self, resp, data_type):
		data = json.loads(resp.json())[data_type]
		return { d['id'] : d for d in data}

	@ns.expect(mail.history)
	@ns.response(201, "Email added to the queue")
	@ns.response(500, "Catalog could not find items")
	#If the item could not be found when __confirming__ it, there sure is an error.
	@ns.response(503, "Could not connect to catalog or database service")
	def post(self):
		data = api.payload
		recipients = list(data['recipients'].values())
		order = data['order']

		rest_ids = ",".join([str(value['rest']) for value in order])
		try:
			resp = get("{}/catalog/id/restaurant?restaurant=({})".format(
							current_app.config["CATALOG_URL"],
							rest_ids
							)
						)
			if resp.status_code == 503:
				return {'message': 'could not stablish connection to database'}, 503
			elif resp.status_code == 404:
				return {'message': 'could not stablish connection to database'}, 500
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to catalog'}, 503

		rest = self.decode(resp, 'restaurant')

		total_value = 0

		msg = template.head
		for rest_order in order:
			rest_id = rest_order['rest']
			meal_keys = ",".join([str(meal['meal']) for meal in rest_order['items']])

			try:
				resp = get("{}/catalog/id/meal?restaurant=({})&meal=({})".format(
						current_app.config["CATALOG_URL"],
						rest_id,
						meal_keys
					),
				)
				if resp.status_code == 503:
					return {'message': 'could not stablish connection to database'}, 503
				elif resp.status_code == 404:
					return {'message': 'could not stablish connection to database'}, 500
			except exceptions.ConnectionError:
				return {'message': 'could not stablish connection to catalog'}, 503

			meal = self.decode(resp, 'meal')

			rest_price = 0
			msg += template.restaurant_body(rest[rest_id]['image'], rest[rest_id]['name'])
			for meal_data in rest_order['items']:
				meal_id = meal_data['meal']
				ammount = meal_data['ammount']
				name = meal[meal_id]['name']
				price = float(meal[meal_id]['price'])

				rest_price += ammount * price

				msg += template.meal_body(name, ammount, price)

			msg += template.restaurant_total(rest_price)

			total_value += rest_price

		taxa = payment.service_fee(total_value)
		msg += template.total(total_value, taxa)

		mail = {
			'subject' : 'Confirmação de pedido',
			'recipients' : recipients,
			'html' : msg
		}

		mail_scheduler.append(mail)
		return {'message' : 'email added to queue'}, 201