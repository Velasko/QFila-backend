from flask import Flask

from flask_restx import Api, Resource

from flask_mail import Mail, Message

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

api = Api(version='0.1', title='Qfila-Mail',
	description='A Mail REST interface for the Qfila application',
)

ns = api.namespace('mail')
mail = Mail()

from . import password_recovery



if __name__ == '__main__':
	app = Flask("Qfila user")
	api.init_app(app)
	mail.init_app(app)
	app.run(debug=True)