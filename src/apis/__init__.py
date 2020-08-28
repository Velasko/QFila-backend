from flask_restx import Api

api = Api(
	title='Qfila'
)

app = None

#create function here for the imports
#it's easier to not add the namespace than to delete
#intention of this 'not adding' is for the capability
#of selecting which services to run.
def config_api(libs):
	import importlib

	if libs is None:
		libs = ('database', 'user')
	try:
		for service_name in libs:
			service = importlib.import_module('.app', f"{__package__}.{service_name}")

			api.add_namespace(service.ns)
			service.ns._path = service_name
	except ModuleNotFoundError as e:
		import sys

		module = e.msg.split('.')[-2]
		if module == 'apis':
			module = e.msg.split('.')[-1][:-1]

		print("There is no service named '{}'".format(module))
		sys.exit()