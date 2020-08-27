import argparse

from . import app

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Execution of full application')

	parser.add_argument('--database', default=None, type=str, help="Database url for connection.")


	group = parser.add_mutually_exclusive_group()
	group.add_argument('-r', '--run', action='store_true', help="Runs the REST application")
	group.add_argument('-t', '--test', action='store_true', help='Runs the unittest')

	parser.add_argument('-d', '--debug', action='store_true', help="Runs with debug")
	parser.add_argument('-p', '--port', default=5000, help="Which port to run the application on")

	args = parser.parse_args()

	if args.database is not None:
		app.config['DATABASE_URL'] = args.database
	else:
		app.config['DATABASE_URL'] = f'http://localhost:{args.port}'

	if args.run:
		app.run(debug=args.debug, port=args.port)
	elif args.test:
		raise NotImplementedError()
	else:
		parser.print_help()