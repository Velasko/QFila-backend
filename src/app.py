from flask import Flask

from .apis import api

app = Flask('Qfila')
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

api.init_app(app)
for ns in api.namespaces:
	ns.app = app

if __name__ == '__main__':
	app.run(debug=True)