import datetime

from flask_restx import Resource, fields
from sqlalchemy import exc

from ..app import DBsession, ns, api
from ..scheme import Base, SentSMS

try:
	from ...utilities.models.phone import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.phone import *

for model in (database_model):
	api.add_model(model.name, model)

@ns.route('/phone')
class PhoneHandler(Resource):

	@ns.doc("Storages the message ID")
	@ns.expect(database_model)
	@ns.response(200, "Data successfully saved.")
	@ns.response(400, "Could not save data. Check 'message' field.")
	@ns.response(409, "Message was already saved before.")
	def post(self):
		if not 'time' in api.payload:
			api.payload['time'] = datetime.datetime.utcnow()
		else:
			datetime.datetime.fromisoformat(api.payload['time'])

		try:
			sms =SentSMS(**api.payload)
		except TypeError:
			return {'message' : 'Parsed invalid fields'}, 400
		except KeyError as e:
			return {'message' : 'Missing required field: {}'.format(e.args[0])}, 400

		with DBsession as session:
			try:
				session.add(sms)
				session.commit()
				return {'message' : "Data successfully saved"}, 200
			except exc.IntegrityError as e:
				return {'message' : 'Message id already in database.'}, 409