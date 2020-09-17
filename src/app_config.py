def config(app):
	app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
	app.config['APPLICATION_HOSTNAME'] = os.getenv('APPLICATION_HOSTNAME')

	app.config['session_ttl'] = 30

	app.config['MAIL_SERVER'] = 'smtp.gmail.com'
	app.config['MAIL_PORT'] = 587
	app.config['MAIL_USE_TLS'] = True
	app.config['MAIL_USE_SSL'] = False
	app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # enter your email here
	app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME') # enter your email here
	app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # enter your password here
