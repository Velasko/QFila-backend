from flask_restx import fields
from flask_restx.model import Model

user = Model("User", {
	'name' : fields.String(description='User name'),
	'email' : fields.String(description='User email'),
	'passwd' : fields.String(description='User password'),
	'birthday' : fields.Date(description='User birthday', dt_format="iso8601"),
	'phone' : fields.String(description='User phone number')
})

meal = Model("Meal", {
	"rest": fields.Integer(required=True, description="Restaurant's id"),
	"description": fields.String(description="Meal's description"),
	"foodtype": fields.String(required=True, description="Meal's type"),
	"section": fields.String(required=True, description="Restaurant's section on which this meal belongs to"),
	"id": fields.Integer(required=True, description="Meal's id"),
	"image": fields.String(description="Meal's image link"),
	"price": fields.Integer(required=True, description="Meal's price"),
	"name": fields.String(description="Meal's name"),
})

restaurant = Model("Restaurant", {
	"image": fields.String(description="Restaurant's logo link"),
	"bank_info": fields.String(required=True, description="Restaurant's bank info"),
	"id": fields.Integer(required=True, description="Restaurant's id"),
	"location": fields.Integer(required=True, description="Restaurant's food court id"),
	"name": fields.String(description="Restaurant's name"),
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