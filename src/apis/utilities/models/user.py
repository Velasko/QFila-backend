from flask_restx import fields
from flask_restx.model import Model

from .database import user, meal, restaurant

id = Model('Identifyiers', {
	'email' : fields.String(required=True, description='User email'),
	'phone' : fields.Integer(description='User phone number')
})

history = Model("History", {
	'meals' : fields.List(fields.Nested(meal)),
	'restaurants' : fields.List(fields.Nested(restaurant))
})