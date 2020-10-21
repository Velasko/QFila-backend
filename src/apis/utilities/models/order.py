from flask_restx import fields
from flask_restx.model import Model

from .mail import recipient_model


meal_info = Model("order.meal", {
	"meal" : fields.Integer(required=True, description="Meal id"),
	"ammount" : fields.Integer(default=1, description="Ammount of this meal ordered", min=1),
	"comments" : fields.String(default="", description="Changes to the desired meal", max_length=255),
})

rest = Model("order.restaurant", {
	"rest" : fields.Integer(required=True, description="Restaurant id"),
	"meals" : fields.List(fields.Nested(meal_info), required=True,
		description="List of meals to be ordered in this restaurant"
	)
})


payment_methods = ('credit', 'debit', 'google_pay', 'apple_pay', 'samsung_pay', 'pix')
payment_model = Model("order.payment", {
	"method" : fields.String(enum=payment_methods),
	"data" : fields.String
})

order_contents = Model("order.contents", {
	"order" : fields.List(fields.Nested(rest), required=True,
		description="The order for each restaurant to be made"
	)
})

order = order_contents.inherit("order", {
	"fee" : fields.Fixed(decimals=2, default=None, min=0,
		description="Raw value for the fee, if applicable"
	),
	"payment" : fields.Nested(payment_model)
})

db_order = order.inherit("order_db", {
	"user" : fields.String(required=True, description="User's email"),
	"time" : fields.DateTime(required=True, description="Time of purchase")
})

mail_order = order_contents.inherit("order_mail", {
	"recipients" : fields.Nested(recipient_model, required=True)
})