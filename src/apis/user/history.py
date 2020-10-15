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

	@authentication.token_required(namespace=ns)
	@ns.response(400, "Invalid request mode")
	@ns.response(503, "Could not stablish connection to database")
	@ns.doc(params={"mode" : "Defines which mode is desired to see the history 'restaurants' or 'meals'"})
	def get(self, user, mode=None):
		"""Get user's recent restaurants or meals"""

		data = {'user' : user['name']}

		if not mode in ('restaurants', 'meals'):
			return {'message' : 'invalid mode'}, 400

		if user['email'] is None:
			#Users MUST have mails or phone, never none
			id_ = user['phone']
			id_name = 'phone'
		else:
			id_ = user['email']
			id_name = 'email'

		try:
			resp = get('{}/database/user/recents/{}/{}/{}'.format(
					current_app.config['DATABASE_URL'], 
					mode,
					id_name,
					id_
				),
				data=json.dumps(data),
				headers=headers.json
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		if resp.status_code != 200:
			# possible errors are either the mode (returns 404)
			# or the payload is invalid.
			# both of which is impossible (mode was verified here and url patternt was followed)
			return {'message' : 'unexpected error'}, 500

		return resp.json()
				
