from flask import Flask

from .app import api

if __name__ == '__main__':
	app = Flask("Qfila user")
	api.init_app(app)
	app.run(debug=True)