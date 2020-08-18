import os
import sys
import argparse

from sqlalchemy import create_engine

from .scheme import Base
from .app import app


DATABASE_ENGINE = os.getenv('DATABASE_ENGINE')

class myfile(list):
	def write(self, data):
		self.append(data)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Declaration of the database scheme of the application')
	parser.add_argument('--database', default=DATABASE_ENGINE,
						type=str, help="Which database the script should run on.")
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--create_scheme', action='store_true', help="Generates the scheme inside the database.")
	group.add_argument('--delete_scheme', action='store_true', help="Deletes the scheme inside the database.")
	group.add_argument('-r', '--run', action='store_true', help="Runs the REST application")
	group.add_argument('-t', '--test', action='store_true', help='Runs the unittest')

	parser.add_argument('-d', '--debug', action='store_true', help="Runs with debug")
	parser.add_argument('-p', '--port', default=5000, help="Which port to run the application on")

	tester = parser.add_subparsers().add_parser("test", help="REST mode arguments")

	args = parser.parse_args()

#	print(args)

	if args.create_scheme:
		engine = create_engine(args.database)
		Base.metadata.create_all(engine)
		print("scheme created")
	elif args.delete_scheme:
		raise NotImplemented("Deletion of scheme not implemented.")
	elif args.run:
		app.run(debug=args.debug, port=args.port)
	elif args.test:

		import multiprocessing
		from .test import *

		flask = multiprocessing.Process(target=app.run, kwargs={'debug':True})
		flask.daemon = True
		flask.start()

		sys.argv.remove('-t')
		# unittest.main(module='database.test')

		_output = sys.stdout

		filename = '/tmp/unittest_output.log'
		with open(filename, 'w') as file:
			sys.stdout = file
			sys.stderr = file
			execute_tests(verbosity=2, exit=False)

		flask.kill()
		flask.join()

		sys.stderr = _output
		sys.stdout = _output

		print("\nUnittest output:")

		with open(filename, 'r') as file:
			for line in file.readlines():
				print(line, end='')

		print("Tests finished.")

	else:
		parser.print_help()