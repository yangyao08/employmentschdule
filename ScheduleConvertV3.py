# -*- coding: utf-8 -*-
"""
Created on Sun Jun 03 16:06:59 2018

@author: yangyao
"""

from sqlalchemy import create_engine
from sqlalchemy import Column, Table, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
import random



engine = create_engine('sqlite:///C:\\Users\\yangyao\\Desktop\\Scheduling Project\\ScheduleV1.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
s = Session() #Connection to the system

###################################################################################################################
#Assignment of difficulty to each type of job
#Level of difficulty needs to be changed
engagediff = {'C1':{'PPA':1,'WACC':1,'Biz Val':1,'Impair':1},'C2':{'PPA':2,\
              'Biz Val':2, 'BM Work':3, 'Others':3}}

###################################################################################################################
#Functions
            
def add_personnel(name,position):
    person = Personnel(name,position)
    s.add(person)
    s.commit()

def leave_personnel(name):
    selected = s.query(Personnel).filter(Personnel.name == name).first() 
    for eachjob in selected.engagements:
        eachjob.requirement += 1
        erefresh(eachjob)
    s.delete(selected) #need to commit?
    s.commit()

def add_engagement(name,jobtype,hours,startdate,enddate,requirement):
    engage = Engagement(name,jobtype,hours,startdate,enddate,requirement)
    s.add(engage)
    s.commit()

def assign(engagename,*personname):
    eselected =  s.query(Engagement).filter(Engagement.name == engagename).first()
    if personname:
        for each in personname:
            pselected = s.query(Personnel).filter(Personnel.name == each).first()
            eselected.priority(pselected)
    eselected.assignment() #might need to do warning beforehand


def pullout_personnel(engagename,personname):
    eselected =  s.query(Engagement).filter(Engagement.name == engagename).first()
    pselected = s.query(Personnel).filter(Personnel.name == personname).first()
    if pselected not in eselected.personnels:
        print("Error: Personnel not found in engagement") #can be better phrased
    else:
        if eselected.difficulty == 1:
            pselected.diff_1 -= 1
        elif eselected.difficulty == 2:
            pselected.diff_2 -= 1
        else:
            pselected.diff_3 -= 1
        eselected.personnels.remove(pselected)
        eselected.requirement += 1
        prefresh(pselected)
        erefresh(eselected)
        s.commit()
        
def end_engagement(engagename):
    eselected = s.query(Engagement).filter(Engagement.name == engagename).first()
    for eachpeeps in eselected.personnels:
        if eselected.difficulty == 1:
            eachpeeps.diff_1 -= 1
        elif eselected.difficulty == 2:
            eachpeeps.diff_2 -= 1
        else:
            eachpeeps.diff_3 -= 1
        eselected.personnels.remove(eachpeeps)
        prefresh(eachpeeps)
    s.delete(eselected) 
    s.commit()

def time_extension(engagename, new_date):
    eselected = s.query(Engagement).filter(Engagement.name == engagename).first()
    eselected.extend_deadline(new_date)

def timecheck(): 
    currentdate = datetime.datetime.today()
    all_engagement = s.query(Engagement).all()
    for each in all_engagement:
        if (currentdate - each.enddate).days > 0:
            for eachpeeps in each.personnels:
                if each.difficulty == 1:
                    eachpeeps.diff_1 -= 1
                elif each.difficulty == 2:
                    eachpeeps.diff_2 -= 1
                else:
                    eachpeeps.diff_3 -= 1
        s.delete(each)
        s.commit()
    all_personnel = s.query(Personnel).all()
    for each in all_personnel:
        prefresh(each)
                
def fired(personname):
    pselected = s.query(Personnel).filter(Personnel.name == personname).first()
    for each in pselected.engagements:
        each.requirement += 1
        each.personnels.remove(pselected)
        erefresh(each)
    s.delete(pselected)
    s.commit()
###################################################################################################################    
#Other purpose function

def prefresh(peeps):
    job = str([each.name for each in peeps.engagements])
    peeps.engagement_lists = job
    s.commit()

def erefresh(job):
    peeps = str([each.name for each in job.personnels])
    job.personnel_list = peeps
    s.commit()
    
    
    
###################################################################################################################
connection = Table('connect',Base.metadata,\
                   Column('person_id', Integer, ForeignKey('people.id')),\
                   Column('engage_id', Integer, ForeignKey('jobs.id')))

###################################################################################################################

class Personnel(Base):
    __tablename__ = 'people'
    
    id = Column(Integer,primary_key = True)
    name = Column(String(50),unique = True)
    position = Column(String(50))
    engagements = relationship('Engagement',secondary=connection, backref='personnels',lazy='dynamic') ##self.engagements
    diff_1 = Column(Integer, default=0)
    diff_2 = Column(Integer, default=0)
    diff_3 = Column(Integer, default=0)
    engagement_lists = Column(String(255), nullable = True)
    #Add list of engagements
    
    
    def __init__(self,name,position):
        self.name = name
        self.position = position
    
        
    #Constraint 1
    #Return a rating on how occupied a person is starting from a given date
    def capacity(self,date):
        relevant = []
        for job in self.engagements:
            if job.enddate>= date:
                relevant.append(job) 
        return sum(list(map(lambda x:x.hours,relevant)))
    
    #Constraint 2
    #Return a rating of how busy a person is starting from a given date
    def busyness(self,date):
        busy = 0
        for each in self.engagements:
            busyratio = each.hours/each.deadline #assume constant throughout all days
            weight = 1/(abs((each.enddate - date).days)+1) #+1 to prevent error
            busy += busyratio*weight 
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
            if job.enddate>= date:
                relevant.append(job) 
        for each in relevant:
            distribution[each.difficulty] += 1 
        return distribution

################################################################################################################            
        

class Engagement(Base):
    #run once is sufficient
    __tablename__ = 'jobs'
    
    id = Column(Integer,primary_key = True)
    name = Column(String(100),unique = True)
    jobtype = Column(String(100))
    difficulty = Column(Integer)
    hours = Column(Float)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    deadline = Column(Integer) #not calculated yet
    requirement = Column(Integer)
    personnel_list = Column(String(255), nullable = True)
    
    def __init__(self,name,jobtype,hours,startdate,enddate,requirement):
        jobtier = jobtype.split(':')
        self.name = name
        self.jobtype = jobtype
        self.difficulty = engagediff[jobtier[0]][jobtier[1]]
        self.hours = hours
        self.startdate = startdate
        self.enddate = enddate
        self.deadline = (enddate-startdate).days + 1
        self.requirement = requirement
    
    def priority(self,person): #wnsure that it is peeps
        if person in self.personnels:
          return person.name + " has been assigned to this engagement"
        elif self.requirement == 0:
          print("Requirement has already been fulfilled")
        else:
          self.personnels.append(person)
          self.requirement -= 1
          if self.difficulty == 1:
              person.diff_1 += 1
          elif self.difficulty == 2:
              person.diff_2 += 1
          else:
              person.diff_3 += 1
          prefresh(person)
          erefresh(self)
          s.commit()
    
    def assignment(self): #alot of work to be done here. cant do the sort
        while self.requirement != 0:
            all_personnel = s.query(Personnel).all()
            filt_personnel = []
            for each in all_personnel:
                if each.name not in [x.name for x in self.personnels]:
                    filt_personnel.append(each)
            #filter bottom 50th percentile 
            ls=[]
            filt_personnel.sort(key = lambda x: x.capacity(self.startdate))
            for free in filt_personnel[:int(0.50*len(all_personnel))+1]: #constraint 1:Capacity
                ls.append(free)
            ls.sort(key=lambda x: x.busyness(self.enddate))
            for slack in ls: #constraint 2: Busyness
                ls=ls[:int(0.50*len(ls))+1]
            ls.sort(key=lambda x: x.diff_scale(self.startdate))
            for k in ls: #constraint 3 Difficulty
                ls=ls[:int(0.50*len(ls))+1]
            selected = random.choice(ls) #Random selection from resultant personnel
            self.requirement -= 1
            self.personnels.append(selected)
            if self.difficulty == 1:
                selected.diff_1 += 1
            elif self.difficulty == 2:
                selected.diff_2 += 1
            else:
                selected.diff_3 += 1
            prefresh(selected)
        erefresh(self)
        print("Requirement has already been fulfilled")
        s.commit()
            
        
    #remove externally
    def extend_deadline(self,new_end_date):
        if new_end_date> self.enddate:
            self.deadline += (new_end_date - self.enddate).days
            self.enddate = new_end_date
        else:
            print("Please check your new end date.")
        s.commit()        
    
################################################################################################################

        
Base.metadata.create_all(engine)


##################################TESTCASE###################################################        
"""
#Part1: Check add personel and engagement
add_personnel('Adam','Associate')
add_personnel('Brock','Senior Associate')
add_personnel('Candy','Associate')
add_personnel('Jamie','Associate')

add_engagement('ProjectA','C1:PPA',60,datetime.date(2018,6,1),datetime.date(2018,6,30),2)
add_engagement('ProjectB','C2:PPA',60,datetime.date(2018,6,1),datetime.date(2018,6,30),2)

#Part2: Check that people can leave (w/o jobs on hand)
#leave_personnel('Jamie')


#Part3: Check assignment works.
#Rmb to check if over assigment will not work
#assign('ProjectA','Adam','Brock')

assign('ProjectB')
assign('ProjectA') 
"""


#Part4: Check fired
#fired('Adam')
#add_personnel('Adam','Associate')

#Part4: Pullout Personnel. CHeck if person not in project
#pullout_personnel('ProjectA','Brock')


#Part5: Time extension
#time_extension('ProjectA',datetime.datetime(2018,7,25))

"""
#6A: Set time before today
A = s.query(Engagement).filter(Engagement.name == "ProjectA").first()
B = s.query(Engagement).filter(Engagement.name == "ProjectB").first()
A.enddate = datetime.datetime(2018,6,3)
B.enddate = datetime.datetime(2018,6,10)
s.commit()
"""



#Part6B: Check timecheck
timecheck()








######################COMMENTS#####################
# To establish the relation, <engagement>.personnels.append(<personnel>)
# To retrieve it back, 
# for smth in <Engagement>.personnels:
# for smth i <Personnel>.engagements
# Find out how store list of names in a column
# Find out 


    
    

