import time
from threading import Thread, Lock

from flask_mail import Message

class MailScheduler(Thread):
	def __init__(self, mail, *args, **kwargs):
		self.lock = Lock()
		self.mails = []
		self.server = mail
		super().__init__(*args, **kwargs)
		self.setDaemon(True)
		self.start()


	def append(self, mail):
		with self.lock:
			self.mails.append(mail)

	def send_mails(self):
		with self.lock:
			with self.server.connect() as conn:
				for mail in self.mails:
					msg = Message(**mail)
					print('sent:', msg)
					# conn.send(msg)
			self.mails = []

	def run(self):
		# self.mails.append({})
		try:
			while True:
				if len(self.mails) > 0:
					self.send_mails()
				time.sleep(10)
		finally:
			self.send_mails()

if __name__ == '__main__':
	x = MailScheduler(None)
	print(dir(x))
