import time
from threading import Thread, Lock

from flask_mail import Message

class MailScheduler(Thread):
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
		self.start()

	def append(self, mail):
		with self.lock:
			self.mails.append(mail)

	def send_mails(self):
		with self.lock:
			with self.app.app_context():
				with self.server.connect() as conn:
					for mail in self.mails:
						msg = Message(**mail)
						# print("email sent to:", mail['email'])
						print('sent:', msg)
						# conn.send(msg)
			self.mails = []

	def run(self):
		try:
			while True:
				time.sleep(60)
				if len(self.mails) > 0:
					self.send_mails()
		finally:
			self.send_mails()
