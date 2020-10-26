import datetime
import re

from flask_restx import Resource, fields
from sqlalchemy import exc

from .app import ns, api, session
from .scheme import *

try:
	from ..utilities import payment
	from ..utilities.models.order import *
except ValueError:
	#If running from inside apis folder
	from utilities import payment
	from utilities.models.order import *

for model in (meal_info, rest, payment_model, order_contents, order, db_order):
	api.add_model(model.name, model)

@ns.route('/user/order')
class CartHandler(Resource):

	@ns.doc("Register order")
	@ns.expect(db_order)
	@ns.response(201, "Method executed successfully.")
	@ns.response(400, "Bad payload")
	@ns.response(409, "This order was already processed")
	def post(self):
		"""Register order"""

		#separating each meal
		order = []
		for data in api.payload['order']:
			restaurant = data['rest']
			meals = data['meals']
			for meal in meals:
				order.append({
					'rest' : restaurant,
					**meal
				})

		try:
			user = session.query(User).filter(User.email == api.payload['user']).first()
			time = datetime.datetime.fromisoformat(api.payload['time'])
			payment_method = api.payload['payment']['method']

			items = []
			total_price = 0
			for item_data in order:
				meal = session.query(Meal).filter(Meal.id == item_data['meal'], Meal.rest==item_data['rest']).first()
				price = meal.price
				item_price = price * getattr(item_data, 'ammount', 1)

				total_price += item_price

				item = Item(user=user.id, time=time, state='awaiting_payment', total_price=item_price, **item_data)
				items.append(item)

			fee = getattr(api.payload, 'fee', payment.service_fee(total_price))

			cart = Cart(time=time, user=user.id, order_total=total_price,
				payment_method=payment_method, qfila_fee=fee
			)
			session.add(cart)
			session.flush()

			for item in items:
				session.add(item)

			session.commit()
			return {}, 201
		except exc.IntegrityError:
			session.rollback()
			return {'message' : 'This order was already made'}, 409
		except exc.DataError as e:
			session.rollback()
			if "Data truncated for column \'payment_method\' at row 1" in e.args[0]:
				return {'message' : "Invalid payment method"}, 400
			raise(e)
		except Exception as e:
			session.rollback()
			raise e
			api.abort(500)