from flask_restx import fields
from flask_restx.model import Model

from .user import meal, restaurant, foodcourt

catalog_response = Model("catalog.response", {
	'meal' : fields.List(fields.Nested(meal)),
	'restaurant' : fields.List(fields.Nested(restaurant)),
	'foodcourt' : fields.List(fields.Nested(foodcourt)),
})

pagination_model = Model("catalog.pagination", {
	'offset' : fields.Integer(required=True, min=0),
	'limit' : fields.Integer(required=True, min=1)
})

catalog_id_model = Model("catalog.id",{
	'meal' : fields.Integer(),
	'restaurant' : fields.Integer(),
	'foodcourt' : fields.Integer()
})

catalog_location = Model("catalog.location", {
	'city' : fields.String(required=True),
	'state' : fields.String(required=True),
	'latitude' : fields.Float(required=True),
	'longitude' : fields.Float(required=True)
})

catalog_query = Model("Catalog.query", {
	'pagination' : fields.Nested(pagination_model, required=True),
	'id' : fields.Nested(catalog_id_model),
	'keyword' : fields.String(),
	'location' : fields.Nested(catalog_location),
	'courts' : fields.Integer(description="ammount of courts allowed in the response")
})