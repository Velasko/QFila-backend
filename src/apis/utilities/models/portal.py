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

#Section models
sections_list = Model("restaurant.sections_list", {
	"sections" : fields.List(fields.String, required=True)
})

section_create = Model("restaurant.section_create", {
	"name" : fields.String(required=True)
})

section_list = Model("restaurant.section_list", {
	"names" : fields.List(fields.String, required=True)
})

section_edit = Model("restaurant.section_edit", {
	"old_name" : fields.String(required=True),
	"new_name" : fields.String(trquired=True)
})

section_items_edit = Model("restaurant.section_items_edit", {
	"section" : fields.String(required=True),
	"meals" : fields.List(fields.Integer, required=True)
})

#Meal models
meal_list = Model("restaurant.meal_list", {
	"meals" : fields.List(fields.Integer()),
})

db_meal_list = meal_list.inherit("db.restaurant.meal_list",{
	"offset" : fields.Integer(default=1),
	"limit" : fields.Integer(default=15)
})

compl_repr = Model("restaurant.complement_meal",{
	"id" : fields.Integer(required=True),
	"ammount" : fields.Integer(delfaut=1)
})

meal_create = Model("restaurant.meal_create", {
	"name" : fields.String,
	"foodtype" : fields.String(),
	"price" : fields.Fixed(decimals=2),
	"description" : fields.String(),
	"image" : fields.String(),
	"available" : fields.Integer(default=0),
	"complements" : fields.List(fields.Nested(compl_repr))
})

meal_edit = Model("restaurant.meal_edit", {
	"meal_id" : fields.Integer(required=True),
	"new_fields" : fields.Nested(meal_create, required=True)
})

# Complement models
complement_list = Model("restaurant.compl_list", {
	"complements" : fields.List(fields.Integer())
})

db_complement_list = Model("restaurant.db_compl_list", {
	"offset" : fields.Integer(default=1),
	"limit" : fields.Integer(default=15)
})

complement_item = Model("restaurant.complement_item",{
	"name" : fields.String(required=True),
	"price" : fields.Fixed(decimals=2)
})

complement_create = Model("restaurant.complement_create", {
	"head" : fields.String(required=True),
	"name" : fields.String(required=True),
	"description" : fields.String,
	"min" : fields.Integer(default=0),
	"max" : fields.Integer(default=1),
	"stackable" : fields.Integer(default=1),
	"items" : fields.List(fields.Nested(complement_item))
})

complements_data = Model("restaurant.complement_return", {
	"complements" : fields.List(fields.Nested(complement_create))
})

complement_edit = Model("restaurant.complement_edit", {
	"complement_id" : fields.Integer(required=True),
	"new_fields" : fields.Nested(complement_create, required=True)
})

complement_delete = complement_list.inherit("restaurant.complement_delete", {
	"force" : fields.Boolean(default=False)
})