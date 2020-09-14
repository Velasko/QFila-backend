def config(app):
	app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
	app.config['APPLICATION_HOSTNAME'] = os.getenv('APPLICATION_HOSTNAME')
	app.config['DATABASE_URI'] = os.getenv('DATABASE_URI')

	app.config['session_ttl'] = 30

	app.config['DATABASE_PAGE_SIZE_DEFAULT'] = 5 
	app.config['DATABASE_PAGE_SIZE_LIMIT'] = 10

	#url.com/test/ and url.com/test will be the same with this argument:
	app.url_map.strict_slashes = False