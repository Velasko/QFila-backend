from flask_restx import fields
from flask_restx.model import Model

recipient_model = Model("phone.recipient", {
	"user" : fields.Integer(required=True, description="User id"),
	"phone" : fields.String(required=True, description="Phone number to send the sms")
})

phone_model = recipient_model.inherit("phone.base", {
})

recover_passwd_model = phone_model.inherit("phone.passwd", {
	'link' : fields.String(required=True)
})

database_model = Model("database.phone", {
	'aws_id' : fields.String(description="AWS message's id", required=True),
	'user_id' : fields.Integer(description="User's id", required=True),
	'time' : fields.DateTime(description="Time the message was sent"),
	'operation' : fields.String(description="The operation which sent the sms")
})