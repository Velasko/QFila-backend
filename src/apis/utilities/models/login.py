from flask_restx import fields
from flask_restx.model import Model

id = Model('Identifyiers', {
	'email' : fields.String(description='User email'),
	'phone' : fields.String(description='User phone number')
})

login_model = id.inherit("user.login", {
	'passwd' : fields.String(required=True, description="User's password")
})

token = Model("token", {
	'token' : fields.String(required=True)
})

passwd = Model("password", {
	'passwd' : fields.String(required=True)
})