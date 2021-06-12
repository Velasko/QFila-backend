from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, checkers, headers
	from ..utilities.models import database, login
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, checkers, headers
	from utilities.models import database, login

for model in (login.id, login.login_model):
	api.add_model(model.name, model)

@ns.route('/login')
class Authenticator(Resource):

	@ns.doc("Portal authentication")
	@ns.expect(login.login_model)
	@ns.response(401, "Authentication failed")
	@ns.response(417, "Expected email or phone; got none.")
	@ns.response(503, "Could not stablish connection to database")
	def post(self):
		"""Method to be authenticated"""

		auth = api.payload
		path = "/database/portal/user/{}/{}"

		return authentication.http_login(path, auth)

@ns.route('/test')
class PageTest(Resource):

	@authentication.token_required(namespace=ns)
	def get(self, user):
		return {}, 200