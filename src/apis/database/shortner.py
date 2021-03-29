import random
import string

import time
from datetime import date
import threading

from flask import current_app
from flask_restx import Resource
from sqlalchemy import exc

from .app import ns, session, api
from .scheme import Shortner

try: 
	from ..utilities.models.shortner import *
	from ..utilities.headers import *
except ValueError:
	from utilities.models.shortner import *
	from utilities import headers

for model in (short_request, short_request_database, short_response, long_request, long_response):
	api.add_model(model.name, model)

characters = string.ascii_letters + "123456789"

@ns.route('/shortner')
class ShortnerHandler(Resource):

	@ns.expect(long_request)
	@ns.response(200, "Successfully found a coresponding URL", model=long_response)
	@ns.response(404, "Could not find url")
	def get(self):
		"""Method to return the full url based on the short one that was passed in the payload"""
		path = api.payload['short_url']
		try:
			query = session.query(Shortner).filter(Shortner.short == path)
			long_url = query.first().serialize()

			return {'long_url' : long_url['long']}, 200
		except AttributeError:
			return {'message' : 'no corresponding url found'}, 404

	@ns.expect(short_request_database)
	@ns.response(200, "Url successfully shortned", model=short_response)
	@ns.response(400, "No possible url to be generated")
	def post(self):
		"""Method to generate a short url"""
		data = api.payload

		if len(data['long_url']) > 511:
			return {'message' : 'long_url too large'}, 400

		if not data['initial_section'].endswith("/"):
			data['initial_section'] += "/"

		path_size = data['max_size'] - len(data['initial_section'])
		if path_size <= 0:
			return {'message' : "initial_section too long or max_size too small"}, 400

		for _ in range(15):
			try:
				short_path = data['initial_section'] + ''.join(random.choice(characters) for _ in range(path_size))
				short = Shortner(
					short=short_path,
					long=data['long_url'],
					delete_time=data['ttl']
				)

				session.add(short)
				session.commit()

				return {'short_url' : short_path}, 200
			except exc.IntegrityError:
				#short url (primary key) already in
				session.rollback()
				print("tried:", short_path)

		return {'message' : 'could not generate an url'}, 500

def url_cleanup():
	import datetime
	while True:
		try:
			now = datetime.datetime.utcnow()
			query = session.query(Shortner).filter(
				Shortner.delete_time < now
			)
			query.delete()
			session.commit()
		except TypeError as e:
			session.rollback()
		except exc.ProgrammingError:
			session.rollback()
		time.sleep(60)

def url_cleanup_daemon():
	t = threading.Thread(target=url_cleanup)
	t.daemon = True
	t.start()