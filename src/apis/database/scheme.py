#Study based on:
#https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
import re

import enum, decimal
from datetime import date

from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy import Float, Integer, SmallInteger, Numeric
from sqlalchemy import String
from sqlalchemy import Date, DateTime
from sqlalchemy import Enum

from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func

Base = declarative_base()

class Tables(list):
	def __init__(self):
		from . import scheme
		for line in open(__file__):
			m = re.match("class (.+)\(Base, Serializable\):*", line)
			if not m is None:
				self.insert(0, getattr(scheme, m.groups()[0]))


def safe_serialize(data):
	data = serialize(data)

	for key in ('login', 'passwd'):
		if key in data:
			del data[key]

	return data

def serialize(data):
	data = {key : value for key, value in data.__dict__.items() if not key.startswith("_")}
	for key, value in data.items():
		if isinstance(value, date): 
			data[key] = value.isoformat()
		elif isinstance(value, enum.Enum):
			data[key] = value.name
		elif isinstance(value, decimal.Decimal):
			data[key] = float(value)

	for key in ('available',):
		if key in data:
			del data[key]

	return data

class Serializable():
	def serialize(self):
		return serialize(self)

	def safe_serialize(self):
		return safe_serialize(self)

class Money(Numeric):
	def __init__(self, *args, **kwargs):
		kwargs['precision'] = 6
		kwargs['scale'] = 2
		super().__init__(*args, **kwargs)

class UserConfirmation(enum.Enum):
	none = 0
	email = 1
	phone = 2
	both = 3

class User(Base, Serializable):
	__tablename__ = 'Users'

	id = Column(Integer, primary_key=True)
	name = Column(String(255))
	birthday = Column(Date)
	email = Column(String(255), unique=True)
	passwd = Column(String(255))
	phone = Column(String(16), unique=True)
	confirmed = Column(Enum(UserConfirmation), nullable=False, default=UserConfirmation(0))

	def __repr__(self):
		return f"User: {self.name}"


class SentSMS(Base, Serializable):
	__tablename__ = 'SentSMS'

	aws_id = Column(String(255), primary_key=True)
	user_id = Column(Integer, ForeignKey('Users.id', ondelete='RESTRICT'), nullable=False)
	time = Column(DateTime, nullable=False)
	operation = Column(String(255))


class FoodCourt(Base, Serializable):
	__tablename__ = 'FoodCourts'

	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False)
	shopping = Column(String(63))
	description = Column(String(255))
	state = Column(String(255), nullable=False) 
	city = Column(String(255), nullable=False)
	address = Column(String(255), nullable=False)
	latitude = Column(Float, nullable=False)
	longitude = Column(Float, nullable=False)

	def __repr__(self):
		return f"Restaurant: {self.name}"


class Restaurant(Base, Serializable):
	__tablename__ = 'Restaurants'

	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False)
	description = Column(String(511))
	bank_info = Column(String(255), nullable=False)
	login = Column(String(255), unique=True, nullable=False)
	passwd = Column(String(255), nullable=False)
	phone = Column(String(16), unique=True)
	location = Column(Integer, ForeignKey('FoodCourts.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
	image = Column(String(200))

	def __repr__(self):
		return f"Restaurant: {self.name}"


class FoodType(Base, Serializable):
	__tablename__ = 'FoodTypes'

	name = Column(String(255), primary_key=True)

	def __repr__(self):
		return f"FoodType: {self.name}"


class Meal(Base, Serializable):
	__tablename__ = 'Meals'

	id = Column(Integer , primary_key=True)
	rest = Column(Integer, ForeignKey('Restaurants.id', ondelete='RESTRICT', onupdate='CASCADE'), primary_key=True)
	name = Column(String(255), nullable=False)
	foodtype = Column(String(255), ForeignKey('FoodTypes.name', ondelete='RESTRICT', onupdate='CASCADE'))
	price = Column(Float, nullable=False)
	description = Column(String(511))
	image = Column(String(200))
	available = Column(SmallInteger, default=0)

	@staticmethod
	def increment(mapper, connection, meal):
		if not meal.id is None:
			return

		from .app import session
		previous = session.query(
			Meal.id
		).filter(
			Meal.rest == meal.rest,
		).order_by(
			Meal.id.desc()
		).first()

		if previous is None:
			meal.id = 1
			return

		meal.id = 1 if not previous[0] else previous[0] + 1

listen(Meal, "before_insert", Meal.increment)

class Complement(Base, Serializable):
	__tablename__= 'Complements'

	id = Column(Integer, primary_key=True)
	rest = Column(Integer, ForeignKey('Restaurants.id', ondelete='CASCADE'), primary_key=True)
	head = Column(String(31), nullable=False) #the 'question'
	description = Column(String(255))
	name = Column(String(15), nullable=False)
	min = Column(SmallInteger, nullable=False, default=0)
	max = Column(SmallInteger, nullable=False, default=1)
	stackable = Column(SmallInteger, default=1) #if the same item can be seleceted multiple times

	@staticmethod
	def before_insert(mapper, connection, complement):
		if (complement.min or 0) > (complement.max or 1):
			raise ValueError("Complement min greater than it's max")


		if not complement.id is None:
			return

		from .app import session
		previous = session.query(
			Complement.id
		).filter(
			Complement.rest == complement.rest
		).order_by(
			Complement.id.desc()
		).first()

		if previous is None:
			complement.id = 1
			return

		complement.id = 1 if not previous[0] else previous[0] + 1

listen(Complement, "before_insert", Complement.before_insert)

class ComplementItem(Base, Serializable):
	__tablename__ = 'ComplementItems'
	__table_args__ = (
		ForeignKeyConstraint(
			['rest', 'compl'],
			['Complements.rest', 'Complements.id'],
			ondelete='CASCADE',
			onupdate='CASCADE'
		),
	)

	rest = Column(Integer, primary_key=True)
	compl = Column(Integer, primary_key=True)
	name = Column(String(15), primary_key=True)
	price = Column(Money, nullable=False)

	available = Column(SmallInteger, default=0)

	def __repr__(self):
		return f"ComplementItem: {self.name}"

	def __eq__(self, other):
		if isinstance(other, str):
			return other.lower() == self.name.lower()
		else:
			return super().__eq__(other)

class MealComplRel(Base, Serializable):
	__tablename__ = 'MealComplementRelationship'
	__table_args__ = (
		ForeignKeyConstraint(
			['rest', 'compl'],
			['Complements.rest', 'Complements.id'],
			ondelete='RESTRICT',
			onupdate='CASCADE'
		),
		ForeignKeyConstraint(
			['rest', 'meal'],
			['Meals.rest', 'Meals.id'],
			ondelete='RESTRICT',
			onupdate='CASCADE'
		),
	)

	rest = Column(Integer, primary_key=True)
	meal = Column(Integer, primary_key=True)
	compl = Column(Integer, primary_key=True)

	ammount = Column(SmallInteger, nullable=False, default=1)


class ComplTag(Base, Serializable):
	__tablename__ = "ComplementTags"
	__table_args__ = (
		ForeignKeyConstraint(
			['rest', 'compl'],
			['Complements.rest', 'Complements.id'],
			ondelete='RESTRICT',
			onupdate='CASCADE'
		),
	)

	rest = Column(Integer, primary_key=True)
	compl = Column(Integer, primary_key=True)
	id = Column(String(16), primary_key=True)

class MenuSection(Base, Serializable):
	__tablename__ = 'MenuSections'
	__table_args__ = (
		UniqueConstraint('rest', 'position'),
	)

	name = Column(String(50), primary_key=True)
	rest = Column(Integer, ForeignKey('Restaurants.id', ondelete='CASCADE'), primary_key=True)
	position = Column(Integer, nullable=False)


class MenuSectionRelation(Base, Serializable):
	__tablename__ = 'MenuSectionsRelationship'
	__table_args__ = (
		ForeignKeyConstraint(
			['rest', 'meal'],
			['Meals.rest', 'Meals.id'],
			ondelete='CASCADE',
			onupdate='CASCADE'
		),

		ForeignKeyConstraint(
			['rest', 'name'],
			['MenuSections.rest', 'MenuSections.name'],
			ondelete='CASCADE',
			onupdate='CASCADE'
		),

		UniqueConstraint('rest', 'name', 'position')
	)

	meal = Column(Integer, primary_key=True)
	rest = Column(Integer, primary_key=True)
	name = Column(String(50), primary_key=True)
	position = Column(Integer, autoincrement=True, nullable=False)

class PaymentMethods(enum.Enum):
	credit = 0
	debit = 1
	google_pay = 2
	apple_pay = 3
	samsung_pay = 4
	pix = 5

class PaymentStatuses(enum.Enum):
	cancelled = -1
	awaiting_availability = 0
	available = 1
	paid = 2

class Cart(Base, Serializable):
	__tablename__ = 'Carts'

	time = Column(DateTime, primary_key=True)
	user = Column(Integer, ForeignKey('Users.id', ondelete='RESTRICT'), primary_key=True)
	price = Column(Money, nullable=False)
	qfila_fee = Column(Money, nullable=False)
	payment_method = Column(Enum(PaymentMethods), nullable=False)
	payment_status = Column(Enum(PaymentStatuses), nullable=False, default=PaymentStatuses(0))


class ItemState(enum.Enum):
	cancelled = -1
	awaiting_payment = 0
	preparing = 1
	served = 2

class Order(Base, Serializable):
	__tablename__ = 'Orders'
	__table_args__ = (
		ForeignKeyConstraint(
			['user', 'time'],
			['Carts.user', 'Carts.time'],
			ondelete='CASCADE',
			onupdate='RESTRICT'
		),
	)

	user = Column(Integer, primary_key=True)
	time = Column(DateTime, primary_key=True)
	rest = Column(Integer, ForeignKey('Restaurants.id', ondelete='RESTRICT', onupdate='CASCADE'), primary_key=True)

	price = Column(Money, nullable=False)
	state = Column(Enum(ItemState), nullable=False)
	comment = Column(String(255))
	rest_order_id = Column(String(16))


class OrderItem(Base, Serializable):
	__tablename__ = 'OrderItems'
	__table_args__ = (
		ForeignKeyConstraint(
			['user', 'time', 'rest'],
			['Orders.user', 'Orders.time', 'Orders.rest'],
			ondelete='RESTRICT',
			onupdate='CASCADE'
		),
		ForeignKeyConstraint(
			['meal', 'rest'],
			['Meals.id', 'Meals.rest'],
			ondelete='RESTRICT',
			onupdate='CASCADE'
		),
	)

	user = Column(Integer, primary_key=True)
	time = Column(DateTime, primary_key=True)
	rest = Column(Integer, primary_key=True)
	meal = Column(Integer, primary_key=True)
	id = Column(SmallInteger, primary_key=True)

	ammount = Column(SmallInteger, nullable=False, default=1)

	price = Column(Money, nullable=False)
	comment = Column(String(255))

	# @staticmethod
	# def increment(mapper, connection, orderitem):

	# 	#The fetch was always empty. Likely because it was trying
	# 	#to add two items in the same commit.
	#	#As I was parsing the id while adding them, I deactivated this code

	# 	from .app import session
	# 	previous = session.query(
	# 		OrderItem
	# 	).filter(
	# 		OrderItem.user == orderitem.user,
	# 		OrderItem.time == orderitem.time,
	# 		OrderItem.rest == orderitem.rest,
	# 		OrderItem.meal == orderitem.meal
	# 	).order_by(
	# 		OrderItem.id
	# 	).all()
	#	# print('next id:', previous[0] + 1 if previous or previous[0] else 1)
	#	# orderitem.id = 1 if not previous[0] else previous[0] + 1

# listen(OrderItem, "before_insert", OrderItem.increment)


class OrderItemComplement(Base, Serializable):
	__tablename__ = 'OrderItemComplement'
	__table_args__ = (
		ForeignKeyConstraint(
			['user', 'time', 'rest', 'meal', 'id'],
			['OrderItems.user', 'OrderItems.time', 'OrderItems.rest', 'OrderItems.meal', 'OrderItems.id'],
			ondelete='CASCADE',
			onupdate='CASCADE'
		),
	)

	user = Column(Integer, primary_key=True)
	time = Column(DateTime, primary_key=True)
	rest = Column(Integer, primary_key=True)
	meal = Column(Integer, primary_key=True)
	id = Column(SmallInteger, primary_key=True)

	data = Column(String(255), primary_key=True)
	price = Column(Money)

class Shortner(Base, Serializable):
	__tablename__ = 'ShortenMap'

	short = Column(String(255), primary_key=True)
	long = Column(String(511), nullable=False)
	delete_time = Column(DateTime, nullable=False)
