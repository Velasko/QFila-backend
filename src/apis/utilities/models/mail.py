from flask_restx import fields
from flask_restx.model import Model

recipient_model = Model("mail.recipient", {
	"name" : fields.String(description="Name to be displayed in the mail"),
	"email" : fields.String(required=True, description="Email address to send the email")
})

email_model = Model("mail.base", {
	'recipients' : fields.List(fields.Nested(recipient_model, required=True), required=True)
})

recover_passwd_model = email_model.inherit("mail.passwd", {
	'link' : fields.String(required=True)
})