import json

from requests import get

from flask_restx import Resource

from .app import ns

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

try:
	from ..utilities import authentication, headers
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, headers

@ns.route("/recent/<string:mode>")
class Recent(Resource):

	@authentication.token_required(appmodule)
	def get(self, user, mode=None):
		"""Get recent restaurants"""

		data = {'user' : user['name']}

		if not mode in ('restaurants', 'meals'):
			api.abort(404)

		resp = get('{}/database/user/history/{}'.format(appmodule.app.config['DATABASE_URL'], mode),
			data=json.dumps(data),
			headers=headers.json
		)

		print(resp.status_code)
		return resp.json()
				
