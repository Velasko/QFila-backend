from flask import Blueprint
from flask_restx import Api, Namespace

blueprint = Blueprint("Qfila client api", __name__)
api = Api(blueprint, version='0.1', title='Qfila user api', default='client',
	description='Client side interface', validate=True
)

ns = Namespace('Client', path='/client', description='client operations')
api.add_namespace(ns)

from . import login
from . import order
from . import history
from . import password_recovery
from . import update