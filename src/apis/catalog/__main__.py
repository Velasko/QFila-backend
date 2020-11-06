import os

from flask import Flask
from flask_cors import CORS

from .app import blueprint
from .config import Config


if __name__ == '__main__':
	import argparse

	app = Flask("Qfila catalog")
	CORS(app)
	config = Config(app)

	parser = argparse.ArgumentParser(description='Catalog interface section of the back-end')

	parser.add_argument('--database', required=True, type=str, help="Database url for connection.")

	group = parser.add_mutually_exclusive_group()
	group.add_argument('-r', '--run', action='store_true', help="Runs the REST application")
	group.add_argument('-t', '--test', action='store_true', help='Runs the unittest')

	parser.add_argument('-d', '--debug', action='store_true', help="Runs with debug")
	parser.add_argument('--host', default='127.0.0.1', help="defines the host")
	parser.add_argument('-p', '--port', default=5000, help="Which port to run the application on")

	args = parser.parse_args()

	app.config['DATABASE_URL'] = args.database

	if args.run:
		app.register_blueprint(blueprint, url_prefix="/")
		config.configure()
		app.run(host=args.host, debug=args.debug, port=args.port)
	elif args.test:
		raise NotImplementedError("Tests for Catalog interface not implemented")
	else:
		parser.print_help()