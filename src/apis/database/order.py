import datetime

from flask_restx import Resource

from .app import ns, api, session
from .scheme import *

@ns.route('/user/order')
class CartHandler(Resource):

	def post(self):
		# order = api.payload['order']
		#separating each meal
		order = []
		for restaurant, meals in api.payload['order'].items():
			for meal, ammount in meals.items():
				order.append({
					'rest' : restaurant,
					'meal' : meal,
					'ammount' : ammount
				})

		try:
			user = session.query(User).filter(User.email == api.payload['user']).first()
			time = datetime.datetime.utcnow()

			items = []
			total_price = 0
			for item_data in order:
				meal = session.query(Meal).filter(Meal.id == item_data['meal'], Meal.rest==item_data['rest']).first()
				price = meal.price
				item_price = price * int(item_data['ammount'])

				total_price += item_price

				item = Item(user=user.id, time=time, state='awaiting_payment', total_price=item_price, **item_data)
				items.append(item)

			cart = Cart(time=time, user=user.id, total_price=total_price)
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