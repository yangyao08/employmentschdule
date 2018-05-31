# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

"""


########### IMPORTED PACKAGE ##########
import datetime                       #
from copy import *                    #
import random                         #
#######################################
   



#Assignment of difficulty to each type of job
#Level of difficulty needs to be changed
engagediff = {'channel 1':{'PPA':1,'WACC':1,'Biz Val':1,'Impair':1},'channel 2':{'PPA':2,\
              'Biz Val':2, 'BM Work':3, 'Others':3}}

#Seperation of each position into tiers
#For future purpose, irrelevant as of Scheduling V2.py
ranking = {'Associate':'Tier1', 'Senior Associate': 'Tier1', 'Manager': 'Tier2', 'Senior Manager':'Tier2'\
           ,'Executive Director':'Tier3','Partner': 'Tier3'} #Tier2 onwards are tentative

############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################

################
#              #
# Personnel    #
#              #
################

class personnel():
    def __init__(self,name,position):
        #name of personnel
        self.name = name 
        
        #Tier of personnel
        #Irrelevant as of Scheduling v2.py
        self.tier = ranking[position]
        
        #List of current/future jobs/engagements assigned
        self.engagements = [] 
        
        #Difficulty distribution of the onhand jobs: Key - 1,2,3 signifies easy,medium, hard
        self.distribution = {1:0,2:0,3:0} 
        
        #Check if the person has been laid-off
        self.left = False 
    
    
    #Display the name of all the jobs on hand e.g. Project Falcon, Project Chinchilla
    def jobs(self): 
        return (list(map(lambda x: x.name,self.engagements)))
    
    
    #Person has left the company
    def laidoff(self): 
        for project in self.engagements:
            project.involved.remove(self)
            project.requirement += 1
        self.left = True
    
    
    #Constraint 1
    #Return a rating on how occupied a person is starting from a given date
    def capacity(self,date):
        relevant = list(filter(lambda x:x.end>=date,self.engagements)) 
        return sum(list(map(lambda x:x.hours,relevant)))
    
    
    #Constraint 2
    #Return a rating of how busy a person is starting from a given date
    def busyness(self,date):
        busy = 0
        for each in self.engagements:
            busyratio = each.hours/each.deadline #assume constant throughout all days
            weight = 1/(abs((each.end - date).days)+1)  ###??? If the job ending soon, larger weightage? Don't make sense
            busy += busyratio*weight #+ 1 above to prevent 1/0
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
        relevant = list(filter(lambda x:x.end>=date,self.engagements))
        for each in relevant:
            self.distribution[each.difficulty] += 1
        return self.distribution
    
    
        
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################

################
#              #
# Engagements  #
#              #
################        
        
class engagement():
    def __init__(self,name,job,hours,start_day,end_day,requirement):
        #Name of engagement
        self.name = name
        
        #Jobs will be in the form of e.g. (channel 1, WACC)
        self.job = job 
        
        #Difficulty of job: easy = 1, medium = 2, hard = 3
        self.difficulty = engagediff[job[0]][job[1]] 
        
        #Expected/allocated hours for the engagement
        self.hours = hours
        
        #Deadline for the engagement
        self.end = end_day
        
        #Starting day of the engagement
        self.start = start_day
        
        #Number of days given for the engagement
        #datetime(yyyy,mm,dd) dif in days
        self.deadline = (end_day-start_day).days 
        
        #Personnels involve in the engagement
        self.involved = []
        
        #Number of personnels required for the engagement
        self.requirement = requirement 
        
        #Check if engagement has ended/is compeleted
        self.complete = False
        
    # Use if a personnel is selected for the engagement
    # Need to check capacity and remind the person if he still want to continue  
    ### Check whether the priority person should/should not be added into the engagementss
    def priority(self,person): 
        if person in self.involved:
          print(person.name + " has been assigned to this engagement")
        elif self.requirement == 0:
          print("Requirement has already been fulfilled")
        else:
          self.involved.append(person)
          person.engagements.append(self)
          self.requirement -= 1
   
    #Random assignment of personnel to the engagement, subject to constraint 1,2 and 3
    def assignment(self,selected_schedule): #TBC
        all_personnel = selected_schedule.allpersonnels  #kapok from schedule
        all_personnel = list(filter(lambda x: x not in self.involved,all_personnel))
        if self.requirement == 0:
          print("Requirement has already been fulfilled")
        while self.requirement != 0:
            #filter bottom 50th percentile 
            ls=[]
            all_personnel.sort(key = lambda x: x.capacity(self.start))
            for free in all_personnel[:int(0.50*len(all_personnel))+1]: #constraint 1:Capacity
                ls.append(free)
            ls.sort(key=lambda x: x.busyness(self.end))
            for slack in ls: #constraint 2: Busyness
                ls=ls[:int(0.50*len(ls))+1]
            ls.sort(key=lambda x: x.diff_scale(self.start))
            for k in ls: #constraint 3 Difficulty
                ls=ls[:int(0.50*len(ls))+1]
            selected = random.choice(ls) #Random selection from resultant personnel
            self.requirement -= 1
            self.involved.append(selected)
            selected.engagements.append(self)
            all_personnel.remove(selected)
        
    #Engagement has been completed 
    ### Factor in force end or deadline end
    def end(self):
        for peeps in self.involved:
            peeps.engagements.remove(self) #remove the job
        self.complete = True
        
    
    #Extension of deadline of the engagement
    def extend_deadline(self,new_end_date):
        self.deadline += (new_end_date - self.end).days
        self.end = new_end_date

############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################

################    
#              #       
# Schedule     #            Functions of the programme
#              #
################        

class schedule():
    def __init__(self):
        #To take in the previously saved file, any future inputs will be done with reference based on this
        self.allpersonnels = []
        self.allengagements = []
        
        #To update the file as of this date
        #self.currentdate = datetime.today() 
    
    #Addition/Hiring of new personnel into the schedule
    def new_personnel(self,newguy):
        self.allpersonnels.append(newguy)
    
    #Personnel left the company
    def layoff_personnel(self,person): #should i put name or person, how do i acccount for it
        person.laidoff()
        self.allpersonnels.remove(person)
        #have to remove it from self.personnels later on through filter, or should i do it now?
    
    #Add new engagement entry into the schedule
    def add_engagement(self,newengagement):
        self.allengagements.append(newengagement)
    
    #Assign personnel into particular engagement
    def assign_engagement(self,selected_engagement,*wanted_personnel):
        if selected_engagement not in self.allengagements:
            return "Remember to add engagement"
        if wanted_personnel:
            for each in wanted_personnel:
                selected_engagement.priority(each)
        if selected_engagement.requirement>0:
            selected_engagement.assignment(self)
        print(list(map(lambda x:x.name,selected_engagement.involved))) #to display who is actually added
    
    #Personnel pulled out from a selected engagement
    def pullout_personnel(self,selected_engagement,selected_personnel):
        if selected_personnel not in selected_engagement.involved:
            return "Error: Personnel not found in engagement" #can be better phrased
        else:
            selected_personnel.engagements.remove(selected_engagement)
            selected_engagement.involved.remove(selected_personnel)
            selected_engagement.requirement += 1
    
    #Forced end an engagement
    def end_engagement(self,selected_engagement):
        selected_engagement.end()
        #filter out those engagement that has ended
    
    #add extension of deadline
        
    def update(): #Update schedule: Personnel & Engagement and saved back for future uses
        #update personnels that are fired/recruited
        #update forced end_engagement
        #Is display a seperate matter?
        pass

############################### Test Case #######################################################

John = personnel('John','Associate')  
Adam = personnel('Adam','Senior Associate')
Mary = personnel('Mary','Associate')
Peter = personnel('Peter','Associate')
Xiaoming = personnel('Xiaoming','Associate')
Xiaochen = personnel('Xiaochen','Senior Associate')
Takagi = personnel('Takagi','Senior Associate')
Hamtaro = personnel('Hamtaro','Senior Associate')
Rajesh = personnel('Rajesh','Associate')


project_A = engagement('projectA',('channel 1','PPA'),60,datetime.date(2018,6,1),datetime.date(2018,7,1),1)
project_B = engagement('projectB',('channel 2','PPA'),80,datetime.date(2018,6,5),datetime.date(2018,7,5),2)
project_C = engagement('projectC',('channel 1','WACC'),60,datetime.date(2018,5,3),datetime.date(2018,5,25),3)
project_D = engagement('projectD',('channel 2','Biz Val'),100,datetime.date(2018,5,3),datetime.date(2018,5,25),3)
project_E = engagement('projectE',('channel 2','Others'),80,datetime.date(2018,5,3),datetime.date(2018,5,25),2)
project_F = engagement('projectF',('channel 1','Impair'),60,datetime.date(2018,5,3),datetime.date(2018,5,25),1)
project_G = engagement('projectG',('channel 1','Impair'),60,datetime.date(2018,5,3),datetime.date(2018,5,25),1)
project_H = engagement('projectH',('channel 2','Others'),80,datetime.date(2018,5,3),datetime.date(2018,5,25),2)
project_I = engagement('projectI',('channel 2','Others'),80,datetime.date(2018,5,3),datetime.date(2018,5,25),2)
project_J = engagement('projectJ',('channel 2','Others'),80,datetime.date(2018,5,3),datetime.date(2018,5,25),1)


#should i do it this way? or create in the new_personnel function
tryout = schedule()
tryout.new_personnel(John)
tryout.new_personnel(Adam)
tryout.new_personnel(Mary)
tryout.new_personnel(Peter)
tryout.new_personnel(Xiaoming)
tryout.new_personnel(Xiaochen)
tryout.new_personnel(Takagi)
tryout.new_personnel(Hamtaro)
tryout.new_personnel(Rajesh)

tryout.add_engagement(project_A) #LOOPHOLE!! Its possible to skip this step and proceed with subsequent
tryout.add_engagement(project_B) #steps. However, it matters! Remember to link the code.
tryout.add_engagement(project_C)



#Test Asignment
ryout.assign_engagement(project_A)
tryout.assign_engagement(project_B, Rajesh)

#Test removal
tryout.pullout_personnel(project_B,Rajesh)
print(list(map(lambda x: x.name,project_B.involved)))

#Test Assignment Distribution
tryout.assign_engagement(project_A)
tryout.assign_engagement(project_B)
tryout.assign_engagement(project_C)
tryout.assign_engagement(project_D)
tryout.assign_engagement(project_E)
tryout.assign_engagement(project_F)
tryout.assign_engagement(project_G)
tryout.assign_engagement(project_H)
tryout.assign_engagement(project_I)
tryout.assign_engagement(project_J)