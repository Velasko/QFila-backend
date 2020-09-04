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
		catalog_re = "((id|name|type)/)?(meal|restaurant|location|all)(/\w+)?"
		compiled_re = re.compile(catalog_re, re.IGNORECASE)
		self.match = lambda string: compiled_re.fullmatch(string)

		super().__init__(*args, **kwargs)

	def get(self, path):
		"""Method to query meals, restaurants and locations"""
		_, category, qtype, keyword = self.match(path.lower()).groups()
		keyword = keyword[1:]


		if qtype == 'all':
			raise NotImplemented("Yet to assemble the junction of queries")
		resp = get(
			'{}/database/catalog'.format(appmodule.app.config['DATABASE_URL']),
			data=json.dumps({
				'category' : category,
				'type' : qtype,
				'keyword' : keyword}),
			headers=headers
		)

		if (code := resp.status_code) != 200:
			api.abort(code)

		return resp.json()



if __name__ == '__main__':
	app = Flask("Qfila catalog")
	api.init_app(app)
	app.run(debug=True)