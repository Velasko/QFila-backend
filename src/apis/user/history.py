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

for model in (recent_model, meal_info, rest, payment_model, order_contents, history_complements, history_items, history_order, history_response, resend_order_model):
	api.add_model(model.name, model)

@ns.route("/recents")
class Recent(Resource):

	@authentication.token_required(namespace=ns)
	@ns.response(200, "Success", model=recent_model)
	@ns.response(503, "Could not stablish connection to database")
	def get(self, user, mode=None):
		"""Get user's recent restaurants"""

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
				headers={**headers.json, **headers.system_authentication}
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		if resp.status_code != 200:
			# possible errors are either the mode (returns 404)
			# or the payload is invalid.
			# both of which is impossible (mode was verified here and url patternt was followed)
			return {'message' : 'unexpected error'}, 500

		return resp.json(), 200
				
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

		#pagination arguments
		offset = int(request.args['pagesize'])*(int(request.args['page']) -1) or 0
		limit = min(
			int(request.args['pagesize'] or current_app.config['CATALOG_PAGE_SIZE_DEFAULT']),
			current_app.config['DATABASE_PAGE_SIZE_LIMIT']
		)

		data = {'user' : user['id'],
				'offset' : offset,
				'limit' : limit,
		}

		try:
			resp = post(
				'{}/database/user/history'.format(
					current_app.config['DATABASE_URL']
				),
				data=json.dumps(data), headers={**headers.json, **headers.system_authentication}
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		if resp.status_code != 200:
			return {'message' : 'unexpected database response'}, resp.status_code
		return resp.json(), 200

	@ns.response(200, "Method executed successfully")
	@ns.response(503, "Could not stablish connection to database or mail service")
	@authentication.token_required(namespace=ns, expect_args=[resend_order_model])
	def post(self, user):
		"""Resends email of the requested order"""

		data = {
			'user' : user['id'],
			'time' : api.payload['time']
		}

		try:
			db_resp = post(
				'{}/database/user/history'.format(
					current_app.config['DATABASE_URL']
				),
				data=json.dumps(data), headers={**headers.json, **headers.system_authentication}
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		mail_model = {
			'recipients' : {"name" : user['name'], "email" : user['email']},
			'order' : db_resp.json()[0]['order']
		}

		for n, rest in enumerate(mail_model['order']):
			for m, meal in enumerate(rest['meals']):
				if meal['comments'] is None:
					del mail_model['order'][n]['meals'][m]['comments']

		try:
			resp = post(
				'{}/mail/orderreview'.format(current_app.config['MAIL_URL']),
				data=json.dumps(mail_model), headers={**headers.json, **headers.system_authentication}
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to mail service'}, 503

		if resp != 201:
			return resp.json()
			return {'message' : 'an error ocurred in the mail service'}, 503

		return {'message' : 'mail successfully sent'}, 200