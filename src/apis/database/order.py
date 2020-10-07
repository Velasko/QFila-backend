import datetime

from flask_restx import Resource, fields

from .app import ns, api, session
from .scheme import *

try:
	from ..utilities import payment
except ValueError:
	#If running from inside apis folder
	from utilities import payment

meal_info = api.model("meal info", {
	"meal" : fields.Integer(required=True, description="Meal id"),
	"ammount" : fields.Integer(required=True, description="Ammount of this meal ordered"),
	"comment" : fields.String(default="", description="Changes to the desired meal"),
})

rest = api.model("restaurant order", {
	"rest" : fields.Integer(required=True, description="restaurant id"),
	"meals" : fields.List(fields.Nested(meal_info), required=True,
		description="List of meals to be ordered in this restaurant"
	)
})

order = api.model("order", {
	"order" : fields.List(fields.Nested(rest), required=True,
		description="The order for each restaurant to be made"
	),
	"fee" : fields.Fixed(decimals=2, default=-1,
		description="Raw value for the fee, if applicable"
	),
	"payment_method" : fields.String
})


@ns.route('/user/order')
class CartHandler(Resource):

	@ns.doc("Register order")
	@ns.expect(order)
	def post(self):
		#separating each meal
		order = []
		for data in api.payload['order'].values():
			restaurant = data['rest']
			meals = data['meals']
			for meal in meals.values():
				order.append({
					'rest' : restaurant,
					**meal
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