import json
import re

from flask import Flask, request
from flask_restx import Api, Resource, fields, reqparse

from requests import post, get, put, delete

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

headers = {
	"accept": "application/json",
	"Content-Type": "application/json"
}

api = Api(version='0.1', title='Catalog',
	description='Client side interface for the catalog',
)

ns = api.namespace('catalog', description='Catalog queries')

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

		Obligatory arguments:
			- latitude : float
			- longitude : float

		Optional arguments:
			- page : int - default=1.
			- pagesize : int - default=5; max=10.

			- city : str - default=fortaleza.
			- state : str - default=ceara.

		Situational arguments:
			if they category is id:
				meal/restaurant/foodcourt is required, depending on desired result;
				expected for it to be integers.
			else:
				keyword is expected.

		The url should be something of the sort:
		http://qfila.com/catalog/{category}/{type}?argument=value
		"""

		catalog_re = "(id|name|type)/(meal|restaurant|location|all)"#(/\w+)?(/page:[0-9]+:[0-9]+)?"
		compiled_re = re.compile(catalog_re, re.IGNORECASE)
		self.match = lambda string: compiled_re.fullmatch(string).groups()

		super().__init__(*args, **kwargs)

	def argument_parser(self, category, **raw_args):
		args = {}

		#pagination
		pagination = {
			'offset' : 0,
			'limit' : appmodule.app.config['DATABASE_PAGE_SIZE_DEFAULT']
		}
		if 'pagesize' in raw_args:
			pagination['limit'] = min(
				int(raw_args['pagesize']),
				appmodule.app.config['DATABASE_PAGE_SIZE_LIMIT']
			)
		if 'page' in raw_args:
			pagination['offset'] = (int(raw_args['page']) - 1) * pagination['limit']
		args['pagination'] = pagination

		#ids/keyword
		if category == 'id':
			args['id'] = {}
			for mrf in ('meal', 'restaurant', 'foodcourt'):
				if mrf in raw_args:
					args['id'][mrf] = int(raw_args[mrf])
				else:
					args['id'][mrf] = None
		else:
			args['keyword'] = raw_args['keyword']

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

		return args

	def get(self, path):
		"""Method to query meals, restaurants and locations"""
		category, qtype = self.match(path.lower())

		try:
			args = self.argument_parser(category, **dict(request.args))
			args['category'] = category
			args['type'] = qtype
		except KeyError as e:
			api.abort(417, "missing argument: " + str(e.args[0]))

		if qtype == 'all':
			raise NotImplemented("Yet to assemble the junction of queries")

		resp = get(
			'{}/database/catalog'.format(appmodule.app.config['DATABASE_URL']),
			data=json.dumps(args),
			headers=headers
		)

		if resp.status_code != 200:
			return { 'message' : 'Error in query'}, resp.status_code

		return resp.json()



if __name__ == '__main__':
	app = Flask("Qfila catalog")
	api.init_app(app)
	app.run(debug=True)