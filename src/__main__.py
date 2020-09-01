import argparse
import sys

from . import app
from .apis import api, config_api

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Execution of full application')


	group = parser.add_mutually_exclusive_group()
	group.add_argument('-r', '--run', action='store_true', help="Runs the full REST application")
	group.add_argument('-t', '--test', action='store_true', help='Runs the unittest')

	parser.add_argument('-d', '--debug', action='store_true', help="Runs with debug")
	parser.add_argument('-p', '--port', default=5000, help="Which port to run the application on")
	parser.add_argument('-s', '--services', nargs='+', help='specifies the REST services to be runned. It is case sensitive!')
	parser.add_argument('--database', default=None, type=str, help="Database url for connection.")

	args = parser.parse_args()

	#If some services are selected,
	#either database is one of those services
	#or the url to access the database must be provided
	if not args.services is None:
		if 'database' in args.services and args.database is None:
			app.config['DATABASE_URL'] = f'http://localhost:{args.port}'
		elif not ('database' in args.services or args.database is None):
			#database is parsed
			app.config['DATABASE_URL'] = args.database
		else:
			print("The database must be one of the services or it's url must be parsed via --database.")
			sys.exit()
	else:
		app.config['DATABASE_URL'] = f'http://localhost:{args.port}'

	config_api(args.services)

	if args.run:
		app.run(debug=args.debug, port=args.port)
	elif args.test:
		raise NotImplementedError()
	else:
		parser.print_help()