from flask_restx import Api

from .database import app as app1
from .user import app as app2

api = Api(
	title='Qfila'
)

api.add_namespace(app1.ns)
api.add_namespace(app2.ns)

app = None