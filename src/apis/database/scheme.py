#Study based on:
#https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/

import enum
from datetime import date

from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy import Float, BigInteger, Integer, SmallInteger 
from sqlalchemy import String
from sqlalchemy import Date, DateTime
from sqlalchemy import Enum

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

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

	return data

class Serializable():
	def serialize(self):
		return serialize(self)

	def safe_serialize(self):
		return safe_serialize(self)


class User(Base, Serializable):
	__tablename__ = 'Users'

	id = Column(Integer, primary_key=True)
	name = Column(String(255))
	birthday = Column(Date)
	email = Column(String(255), unique=True)
	passwd = Column(String(255))
	phone = Column(BigInteger, unique=True)

	def __repr__(self):
		return f"User: {self.name}"

class FoodCourt(Base, Serializable):
	__tablename__ = 'FoodCourts'

	id = Column(Integer	, primary_key=True)
	name = Column(String(255), nullable=False)
	state = Column(String(255), nullable=False) 
	city = Column(String(255), nullable=False)
	address = Column(String(255), nullable=False)
	latitude = Column(Float, nullable=False)
	longitude = Column(Float, nullable=False)

	def __repr__(self):
		return f"Restaurant: {self.name}"

class Restaurant(Base, Serializable):
	__tablename__ = 'Restaurants'

	id = Column(Integer	, primary_key=True)
	name = Column(String(255), nullable=False)
	bank_info = Column(String(255), nullable=False)
	login = Column(String(255), unique=True, nullable=False)
	passwd = Column(String(255), nullable=False)
	location = Column(Integer, ForeignKey('FoodCourts.id', ondelete='RESTRICT'), nullable=False)
	image = Column(String(200))

	def __repr__(self):
		return f"Restaurant: {self.name}"

class FoodType(Base, Serializable):
	__tablename__ = 'FoodTypes'

	name = Column(String(255), primary_key=True)

	def __repr__(self):
		return f"FoodType: {self.name}"

class MenuSection(Base, Serializable):
	__tablename__ = 'MenuSections'

	name = Column(String(50), primary_key=True)
	rest = Column(Integer, ForeignKey('Restaurants.id', ondelete='RESTRICT'), primary_key=True)

class Meal(Base, Serializable):
	__tablename__ = 'Meals'
	__table_args__ = (
		ForeignKeyConstraint(
			['rest', 'section'],
			['MenuSections.rest', 'MenuSections.name'],
			ondelete='RESTRICT'
		),
	)

	id = Column(Integer	, primary_key=True)
	rest = Column(Integer, primary_key=True)
	section = Column(String(50))
	name = Column(String(255), nullable=False)
	foodtype = Column(String(255), ForeignKey('FoodTypes.name', ondelete='RESTRICT'))
	price = Column(Float, nullable=False)
	description = Column(String(511))
	image = Column(String(200))

class PaymentMethods(enum.Enum):
	credit = 0
	debit = 1
	google_pay = 2
	apple_pay = 3
	samsung_pay = 4
	pix = 5

class Cart(Base, Serializable):
	__tablename__ = 'Carts'

	time = Column(DateTime, primary_key=True)
	user = Column(Integer, ForeignKey('Users.id', ondelete='RESTRICT'), primary_key=True)
	order_total = Column(Float, nullable=False)
	qfila_fee = Column(Float, nullable=False)
	payment_method = Column(Enum(PaymentMethods), nullable=False)

class ItemState(enum.Enum):
	cancelled = -1
	served = 0
	preparing = 1
	awaiting_payment = 2

class Item(Base, Serializable):
	__tablename__ = 'Items'
	__table_args__ = (
		ForeignKeyConstraint(
			['user', 'time'],
			['Carts.user', 'Carts.time'],
			ondelete='RESTRICT'
		),
		ForeignKeyConstraint(
			['meal', 'rest'],
			['Meals.id', 'Meals.rest'],
			ondelete='RESTRICT'
		),
	)

	user = Column(Integer, primary_key=True)
	time = Column(DateTime, primary_key=True)
	meal = Column(Integer, primary_key=True)
	rest = Column(Integer, primary_key=True)

	ammount = Column(SmallInteger, nullable=False, default=1)
	state = Column(Enum(ItemState), nullable=False)

	total_price = Column(Float, nullable=False)
	comments = Column(String(255))