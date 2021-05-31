from flask import Blueprint
from flask_restx import Api, Namespace

blueprint = Blueprint("Qfila catalog api", __name__)
api = Api(blueprint, default="catalog", title="Qfila catalog API",
	version="0.1", description="Catalog REST service", validate=True
)

ns = Namespace('Catalog', path='/catalog', description='Catalog queries')
api.add_namespace(ns)

from . import general
from . import restaurant