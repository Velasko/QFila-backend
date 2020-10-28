import os

from flask import Flask
from flask_cors import CORS

from .apis import api

app = Flask('Qfila')
api.init_app(app)

CORS(app, resources={
	r"/catalog/*" : {"origins": "*"},
	r"/user/*" : {"origins": "*"}
})