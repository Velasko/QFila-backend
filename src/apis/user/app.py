from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields

blueprint = Blueprint("Qfila user api", __name__)
api = Api(blueprint, version='0.1', title='Qfila user api', default='user',
	description='Client side interface', validate=True
)

ns = Namespace('user', description='client operations')
api.add_namespace(ns)

from . import login
from . import order
from . import history
from . import password_recovery