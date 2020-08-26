from flask_restx import Api

from .database.app import ns as ns1
from .user.app import ns as ns2

api = Api(
	title='Qfila'
)

api.add_namespace(ns1)
api.add_namespace(ns2)