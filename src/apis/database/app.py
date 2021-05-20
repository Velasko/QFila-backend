import os

from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields

from sqlalchemy import create_engine

from .session import SessionManager
from .scheme import Base

blueprint = Blueprint("Qfila database api", __name__)
api = Api(blueprint, default='database', title="Qfila database api",
	version='0.1', description='Database REST service', validate=True
)

ns = Namespace('database', description="database operations")
api.add_namespace(ns)

engine = create_engine(os.getenv('DATABASE_URI'))
Base.metadata.bind = engine

DBsession = SessionManager(engine)

from . import user
from . import catalog
from . import order
from . import shortner