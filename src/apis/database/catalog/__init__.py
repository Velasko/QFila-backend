from flask_restx import Namespace

from ..app import api

ns = Namespace('Catalog database', path='/database/catalog', description="catalog database operations")
api.add_namespace(ns)

from . import general
from . import restaurant