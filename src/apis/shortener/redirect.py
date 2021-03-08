import json
import requests

from flask import current_app, redirect, request
from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities.models.shortner import *
	from ..utilities import headers
except ValueError:
	#If running from inside apis folder
	from utilities.models.shortner import *
	from utilities import headers

for model in (short_request, short_response, long_request, long_response):
	api.add_model(model.name, model)

@ns.route('/<string:token>')
class ShortResource(Resource):

	@ns.response(503, "Could not stablish connection to database")
	def get(self, token):

		try:
			url = requests.get(
				'{}/database/shortner'.format(current_app.config['DATABASE_URL']),
				data=json.dumps({
					'short_url' : current_app.config['APPLICATION_HOSTNAME'] + "/short/" + token
				}),
				headers={**headers.json, **headers.system_authentication}
			)
		except requests.exceptions.ConnectionError:
			return {'message': 'Could not stablish connection to database'}, 503

		print(url.json())
		path = url.json()['long_url']

		return redirect(path)

parser = ns.parser()
parser.add_argument('security_header', location='headers')

@ns.route('')
class ShortCreation(Resource):

	@ns.expect(parser, short_request)
	def post(self):
		if not 'security_header' in request.headers or request.headers['security_header'] != headers.system_authentication['security_header']:
			return {"message": "Not authorized"}, 403

		try:
			resp = requests.post(
				'{}/database/shortner'.format(current_app.config['DATABASE_URL']),
				data=json.dumps({'initial_section' : (current_app.config['APPLICATION_HOSTNAME'] + "/short/"),
					**api.payload,
				}),
				headers={**headers.json, **headers.system_authentication}
			)

			return resp.json(), resp.status_code

		except requests.exceptions.ConnectionError:
			return {'message': 'Could not stablish connection to database'}, 503
		except Exception as e:
			print(e)
			return {'message': 'unknown error'}, 500