import os

from flask import Flask

from .apis import api

app = Flask('Qfila')

exec(''.join(open('{}/back-end/src/app_config.py'.format(os.getenv('VIRTUAL_ENV')), 'r').readlines()))
config(app)

api.init_app(app)

from .apis.mail import mail
mail.init_app(app)

if __name__ == '__main__':
	app.run(debug=True)