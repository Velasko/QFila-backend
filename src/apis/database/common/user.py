from ..app import DBsession

def fetch_user(user_type, key, value):
	with DBsession as session:
			query = session.query(user_type).filter(
				getattr(user_type, key) == value
			)

			if query.count() == 0:
				return {'message' : 'Restaurant not found'}, 404

			return query.first().serialize()