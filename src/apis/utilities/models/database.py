from flask_restx import fields
from flask_restx.model import Model

user = Model("User", {
	'name' : fields.String(description='User name'),
	'email' : fields.String(description='User email'),
	'passwd' : fields.String(description='User password'),
	'birthday' : fields.Date(description='User birthday', dt_format="iso8601"),
	'phone' : fields.String(description='User phone number')
})

compl_item = Model("Complement.Item", {
	"name" : fields.String(description="Name of the complement's item"),
	"price" : fields.Fixed(decimals=2, description="The price of the complement")
})

complement = Model("Complement", {
	"head" : fields.String(description="The 'question' of the complement"),
	"description" : fields.String(description="A way to give more information to the user"),
	"name" : fields.String(description="A simple name for the restaurant to identify"),
	"min" : fields.Integer(description="Minimal ammount of items to be selected", default=0, min=0),
	"max" : fields.Integer(description="Maximum ammount of items to be selected", default=1, min=1),
	"stackable" : fields.Boolean(description="Defines if the same item can be selected multiple times", default=False),
	"items" : fields.List(fields.Nested(compl_item))
})

meal = Model("Meal", {
	"rest": fields.Integer(required=True, description="Restaurant's id"),
	"description": fields.String(description="Meal's description"),
	"foodtype": fields.String(required=True, description="Meal's type"),
	"section": fields.List(
		fields.String(required=True, 
			description="Restaurant's section on which this meal belongs to"
		)
	),
	"id": fields.Integer(required=True, description="Meal's id"),
	"image": fields.Url(description="Meal's image link"),
	"price": fields.Fixed(decimals=2, required=True, description="Meal's price"),
	"name": fields.String(description="Meal's name"),
	"complements" : fields.List(fields.Nested(complement))
})

restaurant = Model("Restaurant", {
	"image": fields.Url(description="Restaurant's logo link"),
	"description": fields.String(description="Restaurant's description"),
	"bank_info": fields.String(required=True, description="Restaurant's bank info"),
	"id": fields.Integer(required=True, description="Restaurant's id"),
	"location": fields.Integer(required=True,
		description="Restaurant's food court id"
	),
	"name": fields.String(description="Restaurant's name"),
	'phone' : fields.String(description="Restaurant's phone number"),
})

foodcourt = Model("Food Court", {
	'id' : fields.Integer(min=0),
	'name' : fields.String(max_length=255),
	'state' : fields.String(max_length=255),
	'city' : fields.String(max_length=255),
	'address' : fields.String(max_length=255),
	'latitude' : fields.Float(),
	'longitude' : fields.Float()
})