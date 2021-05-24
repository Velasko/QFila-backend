from flask_restx import fields
from flask_restx.model import Model

from .database import user, meal, restaurant
from .order import payment_methods
from .login import *

history_query = Model("history_query", {
	'user' : fields.Integer(required=True, description="User's id"),
	'offset' : fields.Integer(),
	'limit' : fields.Integer(description="total responses"),
	'detailed' : fields.Boolean(default=True, description="if wants object's names and images"),
	'time' : fields.DateTime(description="parse a time if you want a specific response")
})

resend_order_model = Model("resend model", {
	'time' : fields.DateTime(description="time of order")
})

history_complements = Model("history_complements", {
	"price" : fields.Fixed(decimals=2, min=0,
		description="Complements' total price"
	),
	"data" : fields.String(description="Name and ammount of complement")
})

history_items = Model("history_items", {
	"price" : fields.Fixed(decimals=2, min=0,
		description="Item's total price"
	),
	"ammount" : fields.Integer,
	"meal" : fields.Integer(description="Meal's id inside the restaurant"),
	"complements" : fields.List(fields.Nested(history_complements))
})

possible_states = ('cancelled', 'awaiting_payment', 'preparing', 'served')
history_order = Model("history_order",{
	"rest" : fields.Integer,
	"rest_order_id" : fields.String,
	"price" : fields.Fixed(decimals=2, min=0,
		description="Order's total price"
	),
	"state" : fields.String(enum=possible_states),
	"items" : fields.List(fields.Nested(history_items))
})

payment_status = ('cancelled', 'awaiting_availability', 'available', 'paid')
history_response = Model("history_response", {
	"payment_method" : fields.String(enum=payment_methods),
	"qfila_fee" : fields.Fixed(decimals=2, min=0,
		description="Raw value for the fee, if applicable"
	),
	"payment_status" : fields.String(enum=payment_status),
	"price" : fields.Fixed(decimals=2, min=0,
		description="Cart's total price"
	),
	"time" : fields.DateTime(required=True, description="Time of purchase"),
	"orders" : fields.List(fields.Nested(history_order)),
})

user_update = Model("user.update", {
	"old_password" : fields.String(require=True),
	"user" : fields.Nested(user)
})

recent_restaurant = Model("recent.rest", {
	"id": fields.Integer(required=True, description="Restaurant's id"),
	"name": fields.String(description="Restaurant's name"),
	"image": fields.Url(description="Restaurant's logo link"),
	"foodcourt_name" : fields.String(max_length=255),
 	"shopping" : fields.String(max_length=63),
})

recent_model = Model("recent.return", {
	"restaurants" : fields.List(fields.Nested(recent_restaurant))
})