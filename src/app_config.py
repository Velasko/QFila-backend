def config(app):
	app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
	app.config['APPLICATION_HOSTNAME'] = os.getenv('APPLICATION_HOSTNAME')

	app.config['session_ttl'] = 30

	#url.com/test/ and url.com/test will be the same with this argument:
	app.url_map.strict_slashes = False