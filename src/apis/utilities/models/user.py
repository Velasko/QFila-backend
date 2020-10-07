from flask_restx import fields
from flask_restx.model import Model

id = Model('Identifyiers', {
	'email' : fields.String(required=True, description='User email'),
	'phone' : fields.Integer(description='User phone number')
})

user = Model("User", {
	'name' : fields.String(required=True, description='User name'),
	'email' : fields.String(required=True, description='User email'),
	'passwd' : fields.String(required=True, description='User password'),
	'birthday' : fields.Date(required=True, description='User birthday', dt_format="iso8601"),
	'phone' : fields.Integer(description='User phone number')
})

meal = Model("Meal", {
	"id": fields.Integer(required=True, description="Meal's id"),
	"rest": fields.Integer(required=True, description="Restaurant's id"),
	"name": fields.String(description="Meal's name"),
	"foodtype": fields.String(required=True, description="Meal's type"),
	"description": fields.String(description="Meal's description"),
	"section": fields.String(required=True, description="Restaurant's section on which this meal belongs to"),
	"price": fields.Integer(required=True, description="Meal's price"),
	"image": fields.String(description="Meal's image link"),
})

restaurant = Model("Restaurant", {
	"image": fields.String(description="Restaurant's logo link"),
	"bank_info": fields.String(required=True, description="Restaurant's bank info"),
	"id": fields.Integer(required=True, description="Restaurant's id"),
	"location": fields.Integer(required=True, description="Restaurant's food court id"),
	"name": fields.String(description="Restaurant's name"),
})

history = Model("History", {
	'meals' : fields.List(fields.Nested(meal)),
	'restaurants' : fields.List(fields.Nested(restaurant))
})