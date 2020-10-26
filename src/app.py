import os

from flask import Flask

from .apis import api

app = Flask('Qfila')
api.init_app(app)