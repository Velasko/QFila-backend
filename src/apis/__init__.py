from flask_restx import Api

api = Api(
	title='Qfila'
)

#function created for the imports and adding the services to be runned here.
#it's easier to not add the namespace than to delete
#intention of this 'not adding' is for the capability
#of selecting which services to run.
def config_api(app, libs):
	import importlib

	if libs is None:
		libs = ('database', 'user', 'catalog', 'mail')

	try:
		configs = []
		models = api.models
		for service_name in libs:
			service = importlib.import_module('.app', f"{__package__}.{service_name}")

			for name, model in service.api.models.items():
				if name in models:
					raise NameError("Two models with the same name")
				models[name] = model

			app.register_blueprint(service.blueprint, url_prefix=f"/{service_name}")
			api.add_namespace(service.ns)

			if service_name == 'mail':
				service.mail_scheduler.init_app(app)

			config = importlib.import_module('.config', f"{__package__}.{service_name}")
			configs.append(config.Config)

	except ModuleNotFoundError as e:
		import sys

		module = e.msg.split('.')[-2]
		if module == 'apis':
			module = e.msg.split('.')[-1][:-1]

		print("There is no service named '{}'".format(module))
		sys.exit()

	class Config(*configs):
		pass

	return Config(app)