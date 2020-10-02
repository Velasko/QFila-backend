import json

from requests import get

from flask import current_app
from flask_restx import Resource
from flask_mail import Message

from .app import ns, api, mail_scheduler
from . import template

try:
	from ..utilities import headers, payment
except ValueError:
	#If running from inside apis folder
	from utilities import headers, payment

@ns.route('/orderreview')
class OrderReview(Resource):
	def decode(self, resp, data_type):
		data = json.loads(resp.json())[data_type]
		return { str(d['id']) : d for d in data}


	def post(self):
		data = api.payload
		recipients = data['recipients']
		order = data['order']

		rest_ids = ",".join(order.keys())
		resp = get("{}/catalog/id/restaurant?restaurant=({})".format(
						current_app.config["CATALOG_URL"],
						rest_ids
						)
					)
		rest = self.decode(resp, 'restaurant')

		total_value = 0

		msg = template.head
		for rest_id, meals in order.items():
			meal_keys = ",".join(meals.keys())
			resp = get("{}/catalog/id/meal?restaurant={}?meal=({})".format(
					current_app.config["CATALOG_URL"],
					rest_id,
					meal_keys
				),
			)
			meal = self.decode(resp, 'meal')

			rest_price = 0

			msg += template.restaurant_body(rest[rest_id]['image'], rest[rest_id]['name'])
			for meal_id, mealinfo in meals.items():
				ammount = mealinfo['ammount']
				ammt = int(ammount)
				name = meal[meal_id]['name']
				price = float(meal[meal_id]['price'])

				rest_price += ammt * price

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