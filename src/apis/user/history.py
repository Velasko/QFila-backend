import json

from requests import get

from flask import current_app
from flask_restx import Resource

from .app import ns

try:
	from ..utilities import authentication, headers
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, headers

@ns.route("/recent/<string:mode>")
class Recent(Resource):

	@authentication.token_required()
	def get(self, user, mode=None):
		"""Get recent restaurants"""

		data = {'user' : user['name']}

		if not mode in ('restaurants', 'meals'):
			api.abort(404)

		resp = get('{}/database/user/history/{}'.format(current_app.config['DATABASE_URL'], mode),
			data=json.dumps(data),
			headers=headers.json
		)

		return resp.json()
				
