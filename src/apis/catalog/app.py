import json
import re

from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, Namespace, fields, reqparse

from requests import post, get, put, delete

try:
	from ..utilities import headers
except ValueError:
	#If running from inside apis folder
	from utilities import headers


blueprint = Blueprint("Qfila catalog api", __name__)
api = Api(blueprint, default="catalog", title="Qfila catalog API",
	version="0.1", description="Catalog REST service",
)

ns = Namespace('catalog', description='Catalog queries')
api.add_namespace(ns)

# @ns.route('/<string:qtype>')
# @ns.route('/<string:qtype>/<string:keyword>')
# @ns.route('(<string:category>/<string:qtype>/<string:keyword>')
@ns.route('/<path:path>')
class Catalog(Resource):
	def __init__(self, *args, **kwargs):
		"""
		Possible categories of queries:
			- id;
			- name;
			- type.

		Possible types of returns:
			- meal;
			- restaurant;
			- location.

		Optional arguments:
			- keyword : str - default="".
				Used to filter by name or type. If not parsed, will match every possibility.

			- page : int - default=1.
			- pagesize : int - default=5; max=10.

			- city : str - default=fortaleza.
			- state : str - default=ceara.

			- courts : int - default=inf
				Defines the ammount of food courts which should be fetched.

		Situational arguments:
			if they category is id:
				meal/restaurant/foodcourt is required, depending on desired result;
				expected for it to be integers.

			if the query is not id based, the following argument are required:
				- latitude : float
				- longitude : float

		The url should be something of the sort:
		http://qfila.com/catalog/{category}/{type}?argument=value
		"""

		catalog_re = "(id|name|type)/(meal|restaurant|location|all)"
		compiled_re = re.compile(catalog_re, re.IGNORECASE)
		self.match = lambda string: compiled_re.fullmatch(string).groups()

		super().__init__(*args, **kwargs)

	def argument_parser(self, category, **raw_args):
		args = {}

		#pagination
		pagination = {
			'offset' : 0,
			'limit' : current_app.config['DATABASE_PAGE_SIZE_DEFAULT']
		}
		if 'pagesize' in raw_args:
			pagination['limit'] = min(
				int(raw_args['pagesize']),
				current_app.config['DATABASE_PAGE_SIZE_LIMIT']
			)
		if 'page' in raw_args:
			pagination['offset'] = (int(raw_args['page']) - 1) * pagination['limit']
		args['pagination'] = pagination

		#ids/keyword
		if category == 'id':
			args['id'] = {}
			for mrf in ('meal', 'restaurant', 'foodcourt'):
				if mrf in raw_args:
					args['id'][mrf] = raw_args[mrf]
				else:
					args['id'][mrf] = None
		else:
			if 'keyword' in raw_args:
				args['keyword'] = raw_args['keyword']
			else:
				args['keyword'] = ''

			#location
			default = {'city' : 'fortaleza', 'state' : 'ceara'}
			args['location'] = {}
			for loc in ('city', 'state'):
				try:
					args['location'][loc] = raw_args[loc]
				except KeyError:
					args['location'][loc] = default[loc]
			for loc in ('latitude', 'longitude'):
				args['location'][loc] = float(raw_args[loc])

		#food court distance
		args['courts'] = None
		if 'courts' in raw_args:
			args['courts'] = int(raw_args['courts'])

		return args

	def get(self, path):
		"""Method to query meals, restaurants and locations"""
		try:
			category, qtype = self.match(path.lower())

			args = self.argument_parser(category, **dict(request.args))
			args['category'] = category
			args['type'] = qtype
		except AttributeError:
			#re.match returned none -> invalid url
			api.abort(404)
		except KeyError as e:
			api.abort(417, "missing argument: " + str(e.args[0]))

		if qtype == 'all':
			raise NotImplemented("Yet to assemble the junction of queries")

		resp = get(
			'{}/database/catalog'.format(current_app.config['DATABASE_URL']),
			data=json.dumps(args),
			headers=headers.json
		)

		if resp.status_code != 200:
			return { 'message' : 'Error in query'}, resp.status_code

		return resp.json()
