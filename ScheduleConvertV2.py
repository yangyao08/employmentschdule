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


engine = create_engine('sqlite:///C:\\Users\\yangyao\\Desktop\\Scheduling Project\\ScheduleV2.db', echo=False)
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

###################################################################################################################

class Personnel(Base):
    #run once is sufficient
    __tablename__ = 'people'
    
    id = Column(Integer,primary_key = True)
    name = Column(String(50),unique = True)
    position = Column(String(50))
    #engagements = Column(ScalarListType(), nullable=True) #Why nullable? #does this work?
    engagements = relationship('Engagement',secondary=connection, backref='personnels',lazy='dynamic') ##self.engagements
    diff_1 = Column(Integer, default=0)
    diff_2 = Column(Integer, default=0)
    diff_3 = Column(Integer, default=0)
    left = Column(Boolean, default = False)
    
    def __init__(self,name,position):
        self.name = name
        self.position = position
        
    #Constraint 1
    #Return a rating on how occupied a person is starting from a given date
    def capacity(self,date):
        relevant = []
        for job in self.engagements:
            if job.end>= date:
                relevant.append(job) 
        return sum(list(map(lambda x:x.hours,relevant)))
    
    #Constraint 2
    #Return a rating of how busy a person is starting from a given date
    def busyness(self,date):
        busy = 0
        for each in self.engagements:#########filtering not done yet######################!!!!!!!!!!!!!!!!!!
            busyratio = each.hours/each.deadline #assume constant throughout all days
            weight = 1/(abs((each.end - date).days)+1)
            busy += busyratio*weight #+1 to prevent 
        return busy
    
    #Constraint 3A
    #Return a rating of the overall estimated difficulty of the jobs on-hand starting from a given date
    def diff_scale(self,date):
        count=0
        for k,v in self.breakdown(date).items():
            count+=k*v
        return count
    
    #Constraint 3B
    def breakdown(self,date):
        distribution = {1:0,2:0,3:0} 
        relevant = []
        for job in self.engagements:
            if job.end>= date:
                relevant.append(job) 
        for each in relevant:
            distribution[each.difficulty] += 1 #not added in yet###################!!!!!!!!!!!!!!!!!!!!!!!!
        return self.distribution
    
     """

    def laidoff(self):  
        s.delete(self)
        s.commit()
        
      
        if self.engagements:
            for each in self.engagements:
                each.personnels.remove(self)
                each.requirement += 1
        s.delete(self)
        s.commit()
        """

################################################################################################################            
        

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
        
#Base.metadata.drop_all(engine)
"""
Adam = Personnel('Adam',"Associate")
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

#updatepeeps = s.query(Engagement).filter(Engagement.name == 'ProjectA').first()
#updatepeeps.requirement -= 1
#updatepeeps.hours -= 2.0
#s.commit()













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
# Find out how store list of names in a column


    
    

