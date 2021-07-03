import re
from requests import put, exceptions

from flask import current_app

from . import authentication, headers

def modify_user(user, db_url, old_passwd, user_data):
	try:
		authentication.passwd_check(user['passwd'], old_passwd)
	except KeyError:
		return {'message' : 'could not authenticate'}, 401

	if 'id' in user_data:
		del user_data['id']

	if 'passwd' in user_data:
		user_data['passwd'] = authentication.hash_password(user_data['passwd'])

	if 'phone' in user_data and (not re.fullmatch("\+?([0-9]{9,14})", user_data['phone']) is None):
				return {'message' : "Invalid phone number"}, 400

	resp = put(db_url.format(
			current_app.config['DATABASE_URL'],
			user['id_key'],
			user[user['id_key']]
		),
		json=user_data,
		headers={**headers.json, **headers.system_authentication}
	)

	if resp.status_code == 404:
		# this shouldn't happen because token should be invalid
		# if there is no such client.
		return {'message' : 'Unexpected error'}, 500

	return resp.json(), resp.status_code