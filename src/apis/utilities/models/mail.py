from flask_restx import fields
from flask_restx.model import Model

from .user import history_order

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

history = Model("mail.history", {
	"recipients" : fields.Nested(recipient_model, required=True),
	"order" : fields.List(fields.Nested(history_order), required=True,
		description="The order on each restaurant"
	)
})