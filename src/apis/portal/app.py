from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields

blueprint = Blueprint("Qfila portal api", __name__)
api = Api(blueprint, version='0.1', title='Qfila restaurant api', default='rest',
	description='Restaurant side interface', validate=True
)

ns = Namespace('Portal', path='/portal', description='restaurant portal operations')
api.add_namespace(ns)

from . import login
from . import update