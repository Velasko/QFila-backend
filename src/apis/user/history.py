import json

from requests import get, post

from flask import current_app, request
from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, headers
	from ..utilities.models.user import *
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, headers
	from utilities.models.user import *

for model in (meal_info, rest, payment_model, order_contents, history_response):
	api.add_model(model.name, model)

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
				
parser = ns.parser()
parser.add_argument("page", type=int, default=1)
parser.add_argument("pagesize", type=int, default=5)

@ns.route('/history')
class HistoryHandler(Resource):
	
	@ns.response(200, "Method executed successfully", model=history_response)
	@ns.response(503, "Could not stablish connection to database")
	@authentication.token_required(namespace=ns, expect_args=[parser])
	def get(self, user):
		"""Returns the user history"""

		data = {'user' : user['id'],
				'offset' : int(request.args['pagesize'])*(int(request.args['page']) -1),
				'limit' : int(request.args['pagesize']),
		}

		print(json.dumps(data))
		try:
			resp = post(
				'{}/database/user/history'.format(
					current_app.config['DATABASE_URL']
				),
				data=json.dumps(data), headers=headers.json
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		if resp.status_code != 200:
			print(resp.json())
			return {'message' : 'unexpected database response'}, resp.status_code
		return resp.json(), 200
