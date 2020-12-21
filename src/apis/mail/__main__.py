import os

from flask import Flask

from .app import blueprint, mail_scheduler
from .config import Config


if __name__ == '__main__':
	import argparse

	app = Flask("Qfila mail")
	config = Config(app)

	parser = argparse.ArgumentParser(description='User interface section of the back-end')

	group = parser.add_mutually_exclusive_group()
	group.add_argument('-r', '--run', action='store_true', help="Runs the REST application")
	group.add_argument('-t', '--test', action='store_true', help='Runs the unittest')

	parser.add_argument('-d', '--debug', action='store_true', help="Runs with debug")
	parser.add_argument('--host', default='127.0.0.1', help="defines the host")
	parser.add_argument('-p', '--port', default=5000, help="Which port to run the application on")

	for service in ('database', 'catalog'):
		parser.add_argument(f'--{service}', required=True, type=str, help=f"{service} url for connection.")

	args = parser.parse_args()

	app.config['DATABASE_URL'] = args.database
	app.config['CATALOG_URL'] = args.catalog

	if args.run:
		app.register_blueprint(blueprint, url_prefix="/")
		config.configure()
		app.run(host=args.host, debug=args.debug, port=args.port)
	elif args.test:
		raise NotImplementedError("Tests for User interface not implemented")
	else:
		parser.print_help()