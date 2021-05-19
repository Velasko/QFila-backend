import json
import re

from flask import request, current_app
from flask_restx import Resource

from requests import post, exceptions

from .app import api, ns

try:
	from ..utilities import headers
	from ..utilities.models.catalog import *
except ValueError:
	#If running from inside apis folder
	from utilities import headers
	from utilities.models.catalog import *

for model in (compl_item, complement, meal, restaurant, foodcourt, catalog_response):
	api.add_model(model.name, model)

category_doc = """Possible categories of queries:
	- id;
	- name;
	- type."""

type_doc = """Possible types of returns:
	- meal;
	- restaurant;
	- location."""

parser = ns.parser()
parser.add_argument("page", type=int, default=1)
parser.add_argument("pagesize", type=int, default=5)

parser.add_argument("city", default='fortaleza')
parser.add_argument("state", default='ceara')

parser.add_argument("courts", default=5,
	help="Defines the ammount of food courts which should be fetched."
)

id_help = "If it's an id based query, this argument might be required (check at the top). Those arguments are expected to have a parenthesys, to be some sort of list."
parser.add_argument("meal", type=tuple, help=id_help)
parser.add_argument("restaurant", type=tuple, help=id_help)
parser.add_argument("foodcourt", type=tuple, help=id_help)

non_id_help = "If it's **NOT** an id based query, this argument is required."

parser.add_argument("keyword", type=str, default="",
	help=non_id_help + "\nUsed to filter by name or type. If not parsed/empty, will match every possibility. "
)

parser.add_argument('latitude', type=float, help=non_id_help)
parser.add_argument('longitude', type=float, help=non_id_help)

# @ns.route('/<path:path>')
@ns.route('/<string:category>/<string:qtype>')
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
			'limit' : current_app.config['CATALOG_PAGE_SIZE_DEFAULT']
		}
		if 'pagesize' in raw_args:
			pagination['limit'] = min(
				int(raw_args['pagesize']),
				current_app.config['CATALOG_PAGE_SIZE_LIMIT']
			)
		if 'page' in raw_args:
			pagination['offset'] = (int(raw_args['page']) - 1) * pagination['limit']
		args['pagination'] = pagination

		#ids/keyword
		if category == 'id':
			args['id'] = {}
			for mrf in ('meal', 'restaurant', 'foodcourt'):
				if mrf in raw_args:
					if isinstance(raw_args[mrf], str):
						args['id'][mrf]  = [ int(item) for item in  raw_args[mrf].strip("()[]").split(",")]
					elif isinstance(raw_args[mrf], int):
						args['id'][mrf] = [raw_args[mrf]]
					else:
						args['id'][mrf] = raw_args[mrf]
				else:
					args['id'][mrf] = []
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
		if 'courts' in raw_args:
			args['courts'] = int(raw_args['courts'])

		return args

	@ns.doc(params={'category' : category_doc, 'qtype' : type_doc})
	@ns.expect(parser)
	@ns.response(200, "Method executed successfully", model=catalog_response)
	@ns.response(400, "Invalid parsed argument")
	@ns.response(404, "Couldn't find anything")
	@ns.response(503, "Could not stablish connection to database")
	def get(self, category, qtype):
		"""Method to query meals, restaurants and locations

		The url should be something of the sort:
		http://qfila.com/catalog/{category}/{type}?argument=value

		How to use ID on the queries:

			- With MEAL type query:
				- If it's desired to search for a specific meal, parse both meal **and** restaurant's id.
				- If it's desired to fetch a specific part of the restaurant's menu, parse a list of meals ids and a single restaurant's id.
				- If it's desired to get **all** restaurant's meal, parse only the restaurant's.

			- With RESTAURANT type query:
				- If it's desired to search for a specific restaurant, it's only needed to parse the restaurant's id.
				- If it's desired to fetch all restaurants in a food court, parse only the food court's id.

			- With FOODCOURT type query:
				- Parse the food court's id to retrieve.
		"""
		try:
			args = self.argument_parser(category, **dict(request.args))
			args['category'] = category
			args['type'] = qtype
		except AttributeError:
			#re.match returned none -> invalid url
			api.abort(404)
		except KeyError as e:
			api.abort(417, "missing argument: " + str(e.args[0]))
		except ValueError:
			return {'message' : 'An argument is invalid'}, 400


		if qtype == 'all':
			raise NotImplemented("Yet to assemble the junction of queries")

		try:
			resp = post(
				'{}/database/catalog'.format(current_app.config['DATABASE_URL']),
				data=json.dumps(args),
				headers={**headers.json, **headers.system_authentication}
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		if not resp.status_code in (200, 404):
			return { 'message' : 'Unexpected behaviour!' }, 500

		return resp.json(), resp.status_code
