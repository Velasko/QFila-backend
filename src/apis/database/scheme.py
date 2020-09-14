#Study based on:
#https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Float, String, BigInteger
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

class Restaurant(Base, Serializable):
	__tablename__ = 'Restaurants'

	id = Column(Integer	, primary_key=True)
	name = Column(String(255), nullable=False)
	bank_info = Column(String(255), nullable=False)
	login = Column(String(255), unique=True, nullable=False)
	passwd = Column(String(255), nullable=False)
	location = Column(Integer, ForeignKey('FoodCourts.id', ondelete='RESTRICT'), nullable=False)

	def __repr__(self):
		return f"Restaurant: {self.name}"

class FoodType(Base, Serializable):
	__tablename__ = 'FoodTypes'

	name = Column(String(255), primary_key=True)

	def __repr__(self):
		return f"FoodType: {self.name}"


class Meal(Base, Serializable):
	__tablename__ = 'Meals'

	id = Column(Integer	, primary_key=True)
	rest = Column(Integer, ForeignKey('Restaurants.id', ondelete='RESTRICT'), primary_key=True)
	name = Column(String(255), nullable=False)
	foodtype = Column(String(255), ForeignKey('FoodTypes.name', ondelete='RESTRICT'))
	price = Column(Float, nullable=False)
	description = Column(String(511))

class Cart(Base, Serializable):
	__tablename__ = 'Carts'

	time = Column(DateTime, primary_key=True)
	user = Column(Integer, ForeignKey('Users.id', ondelete='RESTRICT'), primary_key=True)
	total_price = Column(Float, nullable=False)
	#trigger total_price = sum(item.price)

class Item(Base, Serializable):
	__tablename__ = 'Items'

	user = Column(Integer, ForeignKey('Carts.user', ondelete='RESTRICT'), primary_key=True)
	time = Column(DateTime, ForeignKey('Carts.time', ondelete='RESTRICT'), primary_key=True)
	rest = Column(Integer, ForeignKey('Meals.rest', ondelete='RESTRICT'), primary_key=True)
	meal = Column(Integer, ForeignKey('Meals.id', ondelete='RESTRICT'), primary_key=True)
	total_price = Column(Float, nullable=False)
