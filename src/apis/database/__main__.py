import os
import sys

from sqlalchemy import create_engine
from flask import Flask

from .scheme import Base

from .app import api

if __name__ == '__main__':
	import argparse
	import importlib

	#package configuration when this is the mainfile execution
	appmodule = importlib.import_module(__package__.split('.')[0])
	app = Flask("Qfila database")

	#adding the configurations from app
	exec(''.join(open("{}/back-end/src/app_config.py".format(os.getenv('VIRTUAL_ENV')), 'r').readlines()))
	config(app)

	api.init_app(app)
	appmodule.app = app


	parser = argparse.ArgumentParser(description='Database section of the application')
	parser.add_argument('--database', type=str, help="Which database the script should run on.")
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--create_scheme', action='store_true', help="Generates the scheme inside the database.")
	group.add_argument('--delete_scheme', action='store_true', help="Deletes the scheme inside the database.")
	group.add_argument('-r', '--run', action='store_true', help="Runs the REST application")
	group.add_argument('-t', '--test', action='store_true', help='Runs the unittest')

	parser.add_argument('-d', '--debug', action='store_true', help="Runs with debug")
	parser.add_argument('-p', '--port', default=5000, help="Which port to run the application on")

#	parser.add_argument('-o', '--output', default=None, help="Recieves the name of the file on which the output will be written to.")

	tester = parser.add_subparsers().add_parser("test", help="REST mode arguments")

	args = parser.parse_args()

	database_url = args.database
	if database_url is None:
		try:
			database_url = os.getenv('DATABASE_URI')
		except:
			print("__main__.py: error: the following arguments are required: --database")
			sys.exit()

	if args.create_scheme:
		engine = create_engine(database_url)
		Base.metadata.create_all(engine)
		print("scheme created")

	elif args.delete_scheme:
		import random, string
		key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(5))
		print('\033[91m' + "WARNING:", '\033[93m',
			'You are about to drop ALL TABLES from the database'
		)

		try:
			confirmation = key#input(f"If you wish to proceed, type: \"{key}\"\033[0m\n>>> ")

			if key != confirmation:
				print("Key incorrect, operation cancelled!")
			else:
				from .scheme import Item, Cart, Meal, MenuSection, FoodType, Restaurant, FoodCourt, User

				for table in (Item, Cart, Meal, MenuSection, FoodType, Restaurant, FoodCourt, User):
					try:
						table.__table__.drop()
					except Exception as e:
						print("An exception has occured with", table.__tablename__)
					else:
						print(table.__tablename__, "dropped")

				print('Scheme has been deleted')
		except KeyboardInterrupt:
			print("Keyboard Interruption! Operation Cancelled.")


	elif args.run:
		app.run(debug=args.debug, port=args.port)
	elif args.test:

		import multiprocessing
		from .test import *

		try:
			flask = multiprocessing.Process(target=app.run, kwargs={'debug':True})
			flask.start()

			sys.argv.remove('-t')

			_output = sys.stdout

			filename = '/tmp/unittest_output.log'
			with open(filename, 'w') as file:
				sys.stdout = file
				sys.stderr = file
				execute_tests(verbosity=2, exit=False)

			sys.stderr = _output
			sys.stdout = _output

			print("\nUnittest output:")

			with open(filename, 'r') as file:
				for line in file.readlines():
					print(line, end='')
		
		finally:
			flask.kill()
			print("Tests finished.")

	else:
		parser.print_help()