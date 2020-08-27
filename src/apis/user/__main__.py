import os

from flask import Flask

from .app import api


if __name__ == '__main__':
	import argparse
	import importlib

	#package configuration when this is the mainfile execution
	appmodule = importlib.import_module(__package__.split('.')[0])
	app = Flask("Qfila user")

	#adding the configurations from app
	exec(''.join(open("{}/back-end/src/app_config.py".format(os.getenv('VIRTUAL_ENV')), 'r').readlines()))
	config(app)

	api.init_app(app)
	appmodule.app = app

	parser = argparse.ArgumentParser(description='User interface section of the back-end')

	parser.add_argument('--database', required=True, type=str, help="Database url for connection.")

	group = parser.add_mutually_exclusive_group()
	group.add_argument('-r', '--run', action='store_true', help="Runs the REST application")
	group.add_argument('-t', '--test', action='store_true', help='Runs the unittest')

	parser.add_argument('-d', '--debug', action='store_true', help="Runs with debug")
	parser.add_argument('-p', '--port', default=5000, help="Which port to run the application on")

	args = parser.parse_args()

	app.config['DATABASE_URL'] = args.database

	if args.run:
		app.run(debug=args.debug, port=args.port)
	elif args.test:
		raise NotImplementedError("Tests for User interface not implemented")
	else:
		parser.print_help()