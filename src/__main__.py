import argparse
import sys

from . import app
from .apis import api, config_api

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Execution of full application')
	required_parse = ("database", "catalog", "mail")

	group = parser.add_mutually_exclusive_group()
	group.add_argument('-r', '--run', action='store_true', help="runs the full REST application")
	group.add_argument('-t', '--test', action='store_true', help='runs the unittest')

	parser.add_argument('-d', '--debug', action='store_true', help="runs with debug")
	parser.add_argument('--host', default='127.0.0.1', help="defines the host")
	parser.add_argument('-p', '--port', default=5000, help="which port to run the application on")
	parser.add_argument('-s', '--services', nargs='+', help='specifies the REST services to be runned. It is case sensitive!')

	for service in required_parse:
		parser.add_argument(f'--{service}', default=None, type=str, help=f"{service} url for connection.")

	args = parser.parse_args()

	#If some services are selected, some depend on secondary services,
	#which must be known where to access.
	#Therefore, either the service is executed here or it's parsed
	for service in required_parse:
		config_name = service.upper() + "_URL"
		if not args.services is None:
			if service in args.services and getattr(args, service) is None:
				#This service is one of the executed ones
				app.config[config_name] = f'http://{args.host}:{args.port}'

			elif not (service in args.services or getattr(args, service) is None):
				#service is parsed
				app.config[config_name] = getattr(args, service)

			else:
				print(f"The {service} must be one of the services or it's url must be parsed via --{service}.")
				sys.exit()
		else:
			#every service is executed
			app.config[config_name] = f'http://{args.host}:{args.port}'

	config = config_api(app, args.services)
	config.configure()

	if args.run:
		app.run(host=args.host, debug=args.debug, port=args.port)
	elif args.test:
		raise NotImplementedError()
	else:
		parser.print_help()