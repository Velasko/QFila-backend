from flask_restx import fields
from flask_restx.model import Model

recipient_model = Model("mail.recipient", {
	'name' : fields.String,
	'email' : fields.String(required=True)
})

email_model = Model("mail.base", {
	'recipients' : fields.List(fields.Nested(recipient_model, required=True), required=True)
})

recover_passwd_model = email_model.inherit("mail.passwd", {
	'link' : fields.String(required=True)
})