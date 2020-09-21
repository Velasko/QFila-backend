def config(app):
	#General configuration
	app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
	app.config['APPLICATION_HOSTNAME'] = os.getenv('APPLICATION_HOSTNAME')
	app.config['session_ttl'] = 30

	#Database configuration
	app.config['DATABASE_URI'] = os.getenv('DATABASE_URI')
	app.config['DATABASE_PAGE_SIZE_DEFAULT'] = 5 
	app.config['DATABASE_PAGE_SIZE_LIMIT'] = 10

	#Mail configuration
	app.config['MAIL_SERVER'] = 'smtp.gmail.com'
	app.config['MAIL_PORT'] = 587
	app.config['MAIL_USE_TLS'] = True
	app.config['MAIL_USE_SSL'] = False
	app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # enter your email here
	app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME') # enter your email here
	app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # enter your password here

	#url.com/test/ and url.com/test will be the same with this argument:
	app.url_map.strict_slashes = False
