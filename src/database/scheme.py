#Study based on:
#https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/

import os
import sys

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'Users'

	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False)
	born = Column(Date, nullable=False)
	email = Column(String(255), unique=True, nullable=False)
	passwd = Column(String(255), nullable=False)
	phone = Column(Integer, unique=True)

class Restaurant(Base):
	__tablename__ = 'Restaurants'

	id = Column(Integer	, primary_key=True)
	name = Column(String(255), nullable=False)
	address = Column(String(255), nullable=False)
	bank_info = Column(String(255), nullable=False)
	login = Column(String(255), unique=True, nullable=False)
	passwd = Column(String(255), nullable=False)

class Meal(Base):
	__tablename__ = 'Meals'

	id = Column(Integer	, primary_key=True)
	rest = Column(Integer, ForeignKey('Restaurants.id'), primary_key=True)
	foodtype = Column(Integer, ForeignKey('FoodTypes.id'))
	price = Column(Float, nullable=False)
	description = Column(String(511))

class FoodType(Base):
	__tablename__ = 'FoodTypes'

	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False)

class Cart(Base):
	__tablename__ = 'Cart'

	user = Column(Integer, ForeignKey('Users.id'), primary_key=True)
	time = Column(DateTime, primary_key=True)
	total_price = Column(Float, nullable=False)
	#trigger total_price = sum(item.price)

class Item(Base):
	__tablename__ = 'Items'

	user = Column(Integer, ForeignKey('Cart.user'), primary_key=True)
	time = Column(DateTime, ForeignKey('Cart.time'), primary_key=True)
	rest = Column(Integer, ForeignKey('Meals.rest'), primary_key=True)
	meal = Column(Integer, ForeignKey('Meals.id'), primary_key=True)
	total_price = Column(Float, nullable=False)