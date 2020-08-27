def config(app):
	app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
	app.config['APPLICATION_HOSTNAME'] = os.getenv('APPLICATION_HOSTNAME')

	app.config['session_ttl'] = 30