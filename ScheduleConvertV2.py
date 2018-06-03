# -*- coding: utf-8 -*-
"""
Created on Sun Jun 03 16:06:59 2018

@author: yangyao
"""

from sqlalchemy import create_engine
from sqlalchemy import Column, Table, Integer, Numeric, String, Unicode, CheckConstraint, Boolean, and_, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship,backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import ScalarListType #what purpose?
import datetime
import random


engine = create_engine('sqlite:///C:\\Users\\yangyao\\Desktop\\Scheduling Project\\ScheduleV2.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
s = Session() #Connection to the system

###################################################################################################################
#Assignment of difficulty to each type of job
#Level of difficulty needs to be changed
engagediff = {'channel 1':{'PPA':1,'WACC':1,'Biz Val':1,'Impair':1},'channel 2':{'PPA':2,\
              'Biz Val':2, 'BM Work':3, 'Others':3}}

###################################################################################################################

connection = Table('connect',Base.metadata,\
                   Column('person_id', Integer, ForeignKey('people.id')),\
                   Column('engage_id', Integer, ForeignKey('jobs.id')))

class Personnel(Base):
    #run once is sufficient
    __tablename__ = 'people'
    
    id = Column(Integer,primary_key = True)
    name = Column(String(50),unique = True) #unique? #in the instance someone have different name, must save it differently
    position = Column(String(50))
    #engagements = Column(ScalarListType(), nullable=True) #Why nullable? #does this work?
    engagements = relationship('Engagement',secondary=connection, backref='personnels',lazy='dynamic')
    diff_1 = Column(Integer, default=0)
    diff_2 = Column(Integer, default=0)
    diff_3 = Column(Integer, default=0)
    left = Column(Boolean, default = False)
    
    def __init__(self,name,position):
        self.name = name
        self.position = position
        ##MISSING
        ##self.tier (removed)
        ##self.engagements
        ##self.distribution
    
         

class Engagement(Base):
    #run once is sufficient
    __tablename__ = 'jobs'
    
    id = Column(Integer,primary_key = True)
    name = Column(String(100),unique = True)
    jobtype = Column(String(100))
    hours = Column(Float)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    deadline = Column(Integer)
    requirement = Column(Integer)
    #personnels = Column(ScalarListType(), nullable=True)
    #personnels = relationship('Personnel',secondary=connection, backref = backref('engagements'))
    completed = Column(Boolean, default = False)
    
    def __init__(self,name,jobtype,hours,startdate,enddate,requirement):
        self.name = name
        self.jobtype = jobtype
        self.hours = hours
        self.startdate = startdate
        self.enddate = enddate
        self.requirement = requirement
        ##MISSING
        ##self.difficulty
        ##self.personnels
        ##self.completed

    

Base.metadata.create_all(engine)


Adam = Personnel('Adam',"Associate")
"""
Brock = Personnel('Brock',"Senior Associate")
Candy = Personnel('Candy',"Associate")

ProjectA = Engagement('ProjectA','C1:PPA',60,datetime.date(2018,6,1),datetime.date(2018,6,30),2)
ProjectB = Engagement('ProjectB','C1:PPA',60,datetime.date(2018,6,1),datetime.date(2018,6,30),2)

s.add(Adam)
s.commit()
s.add(Brock)
s.commit()
s.add(Candy)
s.commit()

s.add(ProjectA)
s.commit()
s.add(ProjectB)
s.commit()


ProjectA.personnels.append(Adam)
ProjectA.personnels.append(Candy)
ProjectB.personnels.append(Adam)
"""




"""

Jamie = Personnel('Jamie',"Associate")
#ProjectA = Engagement('ProjectA','C1:PPA',60,datetime.date(2018,6,1),datetime.date(2018,6,30),2)
s.add(Jamie)
s.commit()
#s.add(ProjectA)
#s.commit()
"""

######################COMMENTS#####################
# To establish the relation, <engagement>.personnels.append(<personnel>)
# To retrieve it back, 
# for smth in <Engagement>.personnels:
# for smth i <Personnel>.engagements


    
    

