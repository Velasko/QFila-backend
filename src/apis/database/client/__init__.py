from flask_restx import Namespace

from ..app import DBsession, api

ns = Namespace('Client database', path='/database/client', description="portal database operations")
api.add_namespace(ns)

from . import client
from . import history
from . import order