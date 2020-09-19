import os

from flask_restx import Api, Resource, fields

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .scheme import Base


api = Api(version='0.1', title='Qfila-Database',
	description='A database REST interface for the Qfila application',
)

ns = api.namespace('database')

engine = create_engine(os.getenv('DATABASE_URI'))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


from . import user
from . import catalog

if __name__ == '__main__':
	from flask import Flask

	app = Flask("Qfila database")
	api.init_app(app)
	app.run(debug=True)