from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields

blueprint = Blueprint("Qfila url shortener api", __name__)
api = Api(blueprint, default='shortener', title="Qfila url shortener api",
	version='0.1', description='Url Shortener REST service', validate=True
)

ns = Namespace('Url shortner', path='/short', description="generates a shortened url")
api.add_namespace(ns)

from . import redirect