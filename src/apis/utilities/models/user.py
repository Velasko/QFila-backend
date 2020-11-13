from flask_restx import fields
from flask_restx.model import Model

from .database import user, meal, restaurant
from .order import *

id = Model('Identifyiers', {
	'email' : fields.String(description='User email'),
	'phone' : fields.Integer(description='User phone number')
})

history = Model("History", {
	'meals' : fields.List(fields.Nested(meal)),
	'restaurants' : fields.List(fields.Nested(restaurant))
})

login_model = id.inherit("user.login", {
	'passwd' : fields.String(required=True, description="User's password")
})

token = Model("token", {
	'token' : fields.String(required=True)
})

passwd = Model("password", {
	'passwd' : fields.String(required=True)
})

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

history_response = order_contents.inherit("history_response", {
	"time" : fields.DateTime(required=True, description="Time of purchase"),
	"qfila_fee" : fields.Fixed(decimals=2, min=0,
		description="Raw value for the fee, if applicable"
	),
	"order_total" : fields.Fixed(decimals=2),
	"payment_method" : fields.String(enum=payment_methods),
})

