from sqlalchemy import create_engine
from sqlalchemy import Column, Table, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
import random



engine = create_engine('sqlite:////home/angps/Documents/Yangyao/webapp/employmentschdule/testing.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
s = Session() #Connection to the system