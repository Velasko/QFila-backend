import datetime

from flask_restx import Resource

from .app import ns, api, session
from .scheme import *

try:
	from ..utilities import payment
except ValueError:
	#If running from inside apis folder
	from utilities import payment

@ns.route('/user/order')
class CartHandler(Resource):

	def post(self):
		#separating each meal
		order = []
		for restaurant, meals in api.payload['order'].items():
			for meal, mealinfo in meals.items():
				order.append({
					'rest' : restaurant,
					'meal' : meal,
					'ammount' : mealinfo["ammount"],
					'comments' : mealinfo["comments"],
				})

		try:
			user = session.query(User).filter(User.email == api.payload['user']).first()
			time = datetime.datetime.utcnow()
			payment_method = api.payload['payment_method']
			fee = api.payload['fee']

			items = []
			total_price = 0
			for item_data in order:
				meal = session.query(Meal).filter(Meal.id == item_data['meal'], Meal.rest==item_data['rest']).first()
				price = meal.price
				item_price = price * int(item_data['ammount'])

				total_price += item_price

				item = Item(user=user.id, time=time, state='awaiting_payment', total_price=item_price, **item_data)
				items.append(item)

			if fee is None:
				fee = payment.service_fee(total_price)

			cart = Cart(time=time, user=user.id, order_total=total_price,
				payment_method=payment_method, qfila_fee=fee
			)
			session.add(cart)
			session.flush()

			for item in items:
				session.add(item)

			session.commit()
		except Exception as e:
			session.rollback()
			raise e
			print("Inside catch")
			api.abort(500)

		return {}, 201