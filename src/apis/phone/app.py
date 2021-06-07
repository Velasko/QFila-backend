import os

from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields

import boto3

from .sender import SMSservice

blueprint = Blueprint("Qfila phone api", __name__)
api = Api(blueprint, default='phone', title="Qfila phone api",
	version='0.1', description='Phone REST service', validate=True
)

ns = Namespace('Phone', path='/phone', description="phone operations")
api.add_namespace(ns)

sns = boto3.client('sns',
	region_name=os.getenv("AWS_Region_name"),
	aws_access_key_id=os.getenv("AWS_Access_key_ID"),
	aws_secret_access_key=os.getenv("AWS_Secret_access_key")
)

sms_service = SMSservice(sns)

from . import password_recovery