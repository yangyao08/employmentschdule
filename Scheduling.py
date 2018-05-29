# -*- coding: utf-8 -*-
"""
Spyder Editor

Project Scheduling
"""

from datetime import datetime
from datetime import timedelta
from copy import *
import random
   

"""
Import previously saved file in here to run
Input paramter interface needed in here<- What should i use, how do i do this?
If time is a new month, import to the next page to print
"""

"""
Inputs:
    Step 1:
        1.Input new engagement:
        2.Change engagement: 
        
    Step 2:
        Ask for: Type of Project, Number of hours, how many personnel needed, personnel(Optional)
                
Note:
    How do i account for at the t=0, where no engagement will be added into it in the first place 
"""


engagediff = {'channel 1':{'PPA':1,'WACC':1,'Biz Val':1,'Impair':1},'channel 2':{'PPA':2,\
              'Biz Val':2, 'BM Work':3, 'Others':3}} #change the level of difficulty

ranking = {'Associate':'Tier1', 'Senior Associate': 'Tier1', 'Manager': 'Tier2', 'Senior Manager':'Tier2'\
           ,'Executive Director':'Tier3','Partner': 'Tier3'} #Tier2 onwards are tentative


class personnel():
    def __init__(self,name,position):
        self.name = name
        self.tier = ranking[position]
        self.engagements = [] #what should be inside/shown
        self.distribution = {1:0,2:0,3:0}#1,2,3 signifies easy,medium and hard project
        self.left = False
    
    def jobs(self): #lsit of jobs taken
        return (list(map(lambda x: x.name,self.engagements)))
        
    def busyness(self,date):
        relevant = list(filter(lambda x:x.end>=date,self.engagements))
        busy = 0
        for each in relevant:
            busyratio = each.hours/each.deadline
            weight = 1/(each.deadline - date)
            busy += busyratio*weight
        return busy
    
    def diff_scale(self,date):
        count=0
        for k,v in self.breakdown(date).items():
            count+=k*v
        return count
            
    def capacity(self,date):
        relevant = list(filter(lambda x:x.end>=date,self.engagements))
        return sum(list(map(lambda x:x.hours,self.engagements)))
    
    def breakdown(self,date):
        relevant = list(filter(lambda x:x.end>=date,self.engagements))
        for each in relevant:
            self.distribution[each.difficulty] += 1
        return self.distribution
    
    def remove(self): #person has left the company
        for project in self.engagements:
            project.involved.remove(self)
        self.left = True
        

class engagement():
    def __init__(self,name,job,hours,start_day,end_day,requirement):
        self.name = name #Job name
        self.job = job #Jobs will be in the form of e.g. (channel 1, WACC)
        self.difficulty = engagediff[job[0]][job[1]] #easy = 1, medium = 2, hard = 3
        self.hours = hours #Number of hours
        self.end = end_day
        self.start = start_day
        self.deadline = (end_day-start_day).days #datetime(yyyy,mm,dd) dif in days
        self.involved = [] #Personnel involve in the engagement
        self.requirement = requirement #number of personnel inside
        self.complete = False
        
    def priority(self,person): #Need to check capacity and remind the person if he still want to continue   
        self.involved.append(person)
        person.engagements.append(self)
        self.requirement -= 1
        
    #Check whether the priority person should/should not be added into the engagementss
    
    def assignment(self):
        avail = deepcopy(listofpersonnel)  #kapok from schedule
        while self.requirement != 0:
            #filter bottom 45th
            ls=[]
            ls2=[]
            for i in sorted_avail[:int(0.5*len(list))]:
                ls.append(i)
            for j in ls.sort(key=lambda x: x.busyness(self.start)):
                ls=ls[:int(0.5*len(ls))]
            for k in ls.sort(key=lambda x: x.diff_scale(self.start)):
                ls=ls[:int(0.5*len(ls))]
            selected = random.choice(ls)
            self.requirement -= 1
            self.involved.append(selected)
            selected.engagements.append(self)
            avail.remove(selected)
            
            
        #take in the schedule and do the necessary calculations here.
        #assign personnel base on the calculation above
        #change persoonnel breakdown
        #change personnel capacity
        #change involved party
        #change engagement
        #change 
    
    def end(self):
        for peeps in self.involved:
            peeps.engagements.remove(self) #remove the job
        self.complete = True
        
    #Factor in force end or deadline end
    
    def extend_deadline(self,new_end_date):
        self.end = new_end_date
        self.deadline += (new_end_date - end_day).days


    
class schedule():
    def __init__(self,name,file):
        #self.time = 
        pass
        
    def update():
        self.time = sg_time
        #How do i create it such that everytime i open it, everything will be up to date as of that time???
        pass
    
    def retrperson(self):
        #retrieve all the staff
    
    def retrengage(self):
        #retrieve all the jobs
    
    #Extract all jobs
    #Extract all personnel
    #Update schedule: Personnel & Engagement
    #Early cut of project and force cut of project
    #Remove person
    
    #replace everyone 
    
    
        
        
        
    
    
        


