import time
import asyncio
from threading import Lock

from flask_mail import Message

class MailScheduler():
	def __init__(self, mail, *args, **kwargs):
		self.lock = Lock()
		self.mails = []
		self.server = mail
		self.app = None

		super().__init__(*args, **kwargs)
		self.daemon = True
		self.name = "Mail sender daemon"

	def init_app(self, app):
		self.app = app
		self.server.init_app(app)

	def append(self, mail):
		with self.lock:
			self.mails.append(mail)

	def send_mails(self):
		with self.lock:
			with self.app.app_context():
				with self.server.connect() as conn:
					for mail in self.mails:
						msg = Message(**mail)
						print("email sent to:", mail['recipients'])
						print(mail['html'])
						# conn.send(msg)
			self.mails = []

	async def main(self):
		try:
			while True:
				await asyncio.sleep(60)
				if len(self.mails) > 0:
					self.send_mails()
		except ConnectionRefusedError as e:
			print(e)
		else:
			if len(self.mails) > 0:
				self.send_mails()
