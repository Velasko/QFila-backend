from flask_restx import fields
from flask_restx.model import Model

restaurant = Model("restaurant.update.base", {
	"image": fields.Url(description="Restaurant's logo link"),
	"description": fields.String(description="Restaurant's description"),
	"bank_info": fields.String(description="Restaurant's bank info"),
	"name": fields.String(description="Restaurant's name"),
	'phone' : fields.String(description="Restaurant's phone number"),
})

rest_update = Model("restaurant.update", {
	"old_password" : fields.String(require=True),
	"rest" : fields.Nested(restaurant)
})

sections_list = Model("restaurant.sections_list", {
	"sections" : fields.List(fields.String, required=True)
})

section_create = Model("Restaurant.section_create", {
	"name" : fields.String(required=True)
})

section_list = Model("Restaurant.section_list", {
	"names" : fields.List(fields.String, required=True)
})

section_edit = Model("Restaurant.section_edit", {
	"old_name" : fields.String(required=True),
	"new_name" : fields.String(trquired=True)
})

section_items_edit = Model("Restaurant.section_items_edit", {
	"section" : fields.String(required=True),
	"meals" : fields.List(fields.Integer, required=True)
})