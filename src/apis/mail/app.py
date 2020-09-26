from flask import Flask

from flask_restx import Api, Resource

from flask_mail import Mail, Message

from .sender import MailScheduler

api = Api(version='0.1', title='Qfila-Mail',
	description='A Mail REST interface for the Qfila application',
)

ns = api.namespace('mail')
mail = Mail()
mail_scheduler = MailScheduler(mail)

from . import password_recovery
from . import order_confirmation



if __name__ == '__main__':
	app = Flask("Qfila user")
	api.init_app(app)
	mail_scheduler.init_app(app)
	app.run(debug=True)