from sqlalchemy.sql.expression import and_

from ..app import session
from ..scheme import *

def fetch_meal_complements(response):
	if not 'meal' in response:
		return 

	for meal in response['meal']:
		complements = []
		meal['complements'] = complements

		compl_query = session.query(
			Complement, MealComplRel.ammount
		).join(
			MealComplRel,
			and_(
				Complement.id == MealComplRel.compl,
				Complement.rest == MealComplRel.rest
			)
		).filter(
			MealComplRel.meal == meal['id'],
			MealComplRel.rest == meal['rest']
		)

		for compl in compl_query:
			compl_data = serialize(compl[0])
			rest, compl_id = compl_data['rest'], compl_data['id']

			item_query = session.query(
				ComplementItem
			).filter(
				ComplementItem.rest == rest,
				ComplementItem.compl == compl_id,
				ComplementItem.available == 1
			)

			compl_data['items'] = [{
				key: value for key, value in item.serialize().items()
					if key not in ('rest', 'id', 'available')
			} for item in item_query]

			compl_data['max'] *= compl[1] #the ammount
			compl_data['min'] *= compl[1]
			complements.append(compl_data)

			del compl_data['rest'], compl_data['id']