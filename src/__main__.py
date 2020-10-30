import argparse
import sys

from . import app
from .apis import api, config_api

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Execution of full application')
	services_list = ("database", "catalog", "mail")

	parser.add_argument('-d', '--debug', action='store_true', help="runs with debug")
	parser.add_argument('--host', default='127.0.0.1', help="defines the host")
	parser.add_argument('-p', '--port', default=5000, help="which port to run the application on")

	group = parser.add_argument_group("Execution mode").add_mutually_exclusive_group()
	group.add_argument('-r', '--run', action='store_true', help="runs the full REST application")
	group.add_argument('-t', '--test', action='store_true', help='runs the unittest')

	ssl_group = parser.add_argument_group('SSL parameters')
	ssl_group.add_argument('--no-ssl', action='store_true', help="Parse it if desired to run without ssl.")
	ssl_group.add_argument('--cert', default='cert.pem', help='certification filename')
	ssl_group.add_argument('--key', default='key.pem', help='key filename')

	service_group = parser.add_argument_group('Service parameters')
	service_group.add_argument('-s', '--services', nargs='+', help='specifies the REST services to be runned. It is case sensitive!')
	for service in services_list:
		service_group.add_argument(f'--{service}', default=None, type=str, help=f"{service} url for connection, if such service not parsed.")

	args = parser.parse_args()

	config = config_api(app, args.services)
	config.configure(auto_verify=False)

	#If some services were selected, there is default url only to those selected.
	#The others will recieve None, which is considered a failure in config.verify() .
	url = f'https://{args.host}:{args.port}'
	if args.services is None:
		args.services = services_list

	for service in services_list: 
		config_name = service.upper() + "_URL"
		if service in args.services:
			app.config[config_name] = url
		else:
			app.config[config_name] = getattr(args, service)

	try:
		config.verify()
	except KeyError as e:
		#if service url was not parsed:
		service = e.key.lower().split("_")[0]
		if service in services_list:
			print(f"The {service} must be one of the services or it's url must be parsed via --{service}.")
			sys.exit()

		raise e

	#if desired to use ssl
	ssl_kwargs = {
		'ssl_context' : (
			"{}/{}".format(config.env_folder(), args.cert),
			"{}/{}".format(config.env_folder(), args.key))
	} if not args.no_ssl else {}

	if args.run:
		app.run(host=args.host, debug=args.debug, port=args.port, **ssl_kwargs)
	elif args.test:
		raise NotImplementedError()
	else:
		parser.print_help()