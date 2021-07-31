from flask_restx import Namespace

from ..app import DBsession, api

ns = Namespace('Portal database', path='/database/portal', description="portal database operations")
api.add_namespace(ns)

from . import auth
from . import complements
from . import meals
from . import sections