from pathlib import Path

from flask_restx import Api

api = Api(
	title='Qfila', 
	validate=True
)

#function created for the imports and adding the services to be runned here.
#it's easier to not add the namespace than to delete
#intention of this 'not adding' is for the capability
#of selecting which services to run.
def config_api(app, libs):
	import importlib

	folder_exceptions = ('__pycache__', 'utilities')

	if libs is None:
		path = Path("src/apis")
		libs = [dir.name for dir in path.iterdir() if dir.is_dir() and not dir.name in folder_exceptions]

	try:
		configs = []
		models = api.models
		for service_name in libs:
			service = importlib.import_module('.app', f"{__package__}.{service_name}")

			for name, model in service.api.models.items():
				if name in models:
					continue
				models[name] = model

			app.register_blueprint(service.blueprint, url_prefix=f"/{service_name}")

			# api.add_namespace(service.ns)
			for ns in service.api.namespaces[1:]:
				api.add_namespace(ns)

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