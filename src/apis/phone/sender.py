import datetime
import requests

import boto3
from botocore.exceptions import ClientError

from flask import current_app

try:
	from ..utilities import headers
except ValueError:
	#If running from inside apis folder
	from utilities import headers

class SMSservice():
	def __init__(self, sns, *args, **kwargs):
		self.server = sns

	def send_message(self, message, phone, client, operation=""):
		if len(message) > 1000:
			raise ValueError("Message too long")

		try:
			print(phone, message)
			return {'message' : "sms sent mocked"}, 200
			response = sns.publish(Message=message, PhoneNumber=phone)
			message_id = response['MessageId']

			requests.put(
				'{}/database/'.format(current_app.config['DATABASE_URL']),
				data={
					'aws_id' : message_id,
					'client_id' : client,
					'time' : datetime.datetime.utcnow().isoformat(),
					'operation' : operation
				},
				headers = {**headers.json, **headers.system_authentication}
			)

			return {
				'message' : "SMS successfully sent",
				'sms id' : message_id
				}, 201
		except ClientError:
			return {'message' : "SMS host could not send the message"}, 424
		except requests.exceptions.ConnectionError:
			return {'message' : 'SMS successfully sent'}, 206