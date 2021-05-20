import asyncio
import datetime

from .app import DBsession

async def url_cleanup():
	while True:
		with DBsession as session:
			try:
				now = datetime.datetime.utcnow()
				query = session.query(Shortner).filter(
					Shortner.delete_time < now
				)
				query.delete()
				session.commit()
			# except TypeError as e:
			# 	session.rollback()
			# except exc.ProgrammingError:
			# 	session.rollback()

		await asyncio.sleep(60)