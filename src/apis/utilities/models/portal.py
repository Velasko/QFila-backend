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