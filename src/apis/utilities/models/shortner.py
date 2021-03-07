from flask_restx import fields
from flask_restx.model import Model

short_request = Model('Short url request',{
	'long_url' : fields.String(required=True, max=511),
	'ttl' : fields.DateTime(description="Time to live/when it's supposed to be deleted"),
	'max_size' : fields.Integer(default=140, description=""),
})

short_request_database = short_request.inherit('db.short_request', {
	'initial_section' : fields.String(required=True)
})

short_response = Model('Short url response',{
	'long_url' : fields.String(required=True)
})

long_request = Model('Long url request',{
	'short_url' : fields.String(required=True),
})

long_response = Model('Long url response',{
	'long_url' : fields.String(required=True)
})