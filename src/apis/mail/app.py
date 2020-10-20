from flask import Blueprint
from flask_restx import Api, Resource, Namespace
from flask_mail import Mail, Message

from .sender import MailScheduler

blueprint = Blueprint("Qfila mail api", __name__)
api = Api(blueprint, version='0.1', title='Qfila-Mail',
	description='A Mail REST interface for the Qfila application', validate=True
)

ns = Namespace('mail', description="Mail service")
api.add_namespace(ns)

mail = Mail()
mail_scheduler = MailScheduler(mail)

from . import password_recovery
from . import order_confirmation