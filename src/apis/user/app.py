from flask_restx import Api, Resource, fields

api = Api(version='0.1', title='Client',
	description='Client side interface',
)

ns = api.namespace('user', description='client operations')


from . import login
from . import order
from . import history
from . import password_recovery


if __name__ == '__main__':
	from flask import Flask
	app = Flask("Qfila user")
	api.init_app(app)
	app.run()